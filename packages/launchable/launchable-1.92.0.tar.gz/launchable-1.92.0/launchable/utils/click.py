import re
import sys
from typing import Dict, Optional

import click

# click.Group has the notion of hidden commands but it doesn't allow us to easily add
# the same command under multiple names and hide all but one.


class GroupWithAlias(click.Group):
    def __init__(self, name: Optional[str] = None, commands: Optional[Dict[str, click.Command]] = None, **attrs):
        super().__init__(name, commands, **attrs)
        self.aliases: Dict[str, str] = {}

    def get_command(self, ctx: click.core.Context, cmd_name: str):
        return super().get_command(ctx, cmd_name) or self.aliases.get(cmd_name)

    def add_alias(self, name: str, cmd: str):
        self.aliases[name] = cmd


class PercentageType(click.ParamType):
    name = "percentage"

    def convert(self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]):
        try:
            if value.endswith('%'):
                x = float(value[:-1]) / 100
                if 0 <= x <= 100:
                    return x
        except ValueError:
            pass

        self.fail("Expected percentage like 50% but got '{}'".format(value), param, ctx)


class DurationType(click.ParamType):
    name = "duration"

    def convert(self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]):
        try:
            return convert_to_seconds(value)

        except ValueError:
            pass

        self.fail("Expected duration like 3600, 30m, 1h15m but got '{}'".format(value), param, ctx)


class KeyValueType(click.Option):
    '''
    Handles options that take key/value pairs.

    The preferred syntax is "--option key=value" and that's what we should be advertising in docs and help,
    but for compatibility (?) we accept other forms of "--option key:value" or "--option key value"
    '''
    error_message = "Expected a key-value pair formatted as --option key=value, --option key:value, " \
                    "or --option key value, but got '{}'"

    def __init__(self, *args, **kwargs):
        super(KeyValueType, self).__init__(*args, **kwargs)
        self._previous_parser_process = None
        self._key_value_parser = None

    def add_to_parser(self, parser, ctx: click.core.Context):
        def parser_process(value, state):
            # case: --option key=value
            if '=' in value:
                kv = value.split('=')
                if len(kv) != 2:
                    raise ValueError(self.error_message.format(value))

                value = tuple([kv[0].strip(), kv[1].strip()])
            # case: --option key:value
            elif ':' in value:
                kv = value.split(':')
                if len(kv) != 2:
                    raise ValueError(self.error_message.format(value))

                value = tuple([kv[0].strip(), kv[1].strip()])
            # case: --option key value
            else:
                rargs = state.rargs
                # --option key-only
                if len(rargs) < 1:
                    raise ValueError(self.error_message.format(value))
                # --option key --other-option / -option key - other-argument
                elif 0 < len(rargs) and any(rargs[0].startswith(p) for p in self._key_value_parser.prefixes):
                    raise ValueError(self.error_message.format(" ".join([value, rargs[0]])))

                value = [value, state.rargs.pop(0)]

            self._previous_parser_process(tuple([value[0], value[1]]), state)

        retval = super(KeyValueType, self).add_to_parser(parser, ctx)
        for name in self.opts:
            our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
            if our_parser:
                self._key_value_parser = our_parser
                self._previous_parser_process = our_parser.process
                our_parser.process = parser_process
                break

        return retval


class FractionType (click.ParamType):
    name = "fraction"

    def convert(self, value: str, param: Optional[click.core.Parameter], ctx: Optional[click.core.Context]):
        try:
            v = value.strip().split('/')
            if len(v) == 2:
                n = int(v[0])
                d = int(v[1])

                return (n, d)

        except ValueError:
            pass

        self.fail("Expected fraction like 1/2 but got '{}'".format(value), param, ctx)


PERCENTAGE = PercentageType()
DURATION = DurationType()
FRACTION = FractionType()

# Can the output deal with Unicode emojis?
try:
    '\U0001f389'.encode(sys.stdout.encoding or "ascii")
    # If stdout encoding is unavailable, such as in case of pipe, err on the safe side (EMOJI=False)
    # This is a judgement call, but given that emojis do not serve functional purposes and purely decorative
    # erring on the safe side seems like a reasonable call.
    EMOJI = True
except UnicodeEncodeError:
    EMOJI = False


def emoji(s: str, fallback: str = ''):
    """
    Used to safely use Emoji where we can.

    Returns 's' in an environment where stdout can deal with emojis, but 'fallback' otherwise.
    """
    return s if EMOJI else fallback


def convert_to_seconds(s: str):
    units = {'s': 1, 'm': 60, 'h': 60 * 60, 'd': 60 * 60 * 24, 'w': 60 * 60 * 24 * 7}

    if s.isdigit():
        return float(s)

    duration = 0
    for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', s, flags=re.I):
        val = m.group('val')
        unit = m.group('unit')

        if val is None or unit is None:
            raise ValueError("unable to parse: {}".format(s))

        u = units.get(unit)
        if u is None:
            raise ValueError("unable to parse: {}".format(s))

        duration += int(val) * u

    return float(duration)


def ignorable_error(e: Exception):
    return "An error occurred on Launchable CLI. You can ignore this message since the process will continue. Error: {}".format(e)

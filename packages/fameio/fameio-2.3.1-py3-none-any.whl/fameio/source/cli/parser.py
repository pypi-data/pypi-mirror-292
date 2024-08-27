# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import copy
from argparse import ArgumentParser, ArgumentTypeError, BooleanOptionalAction, Namespace
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from fameio.source.cli.options import MergingOptions, TimeOptions, ResolveOptions, Options
from fameio.source.logs import LogLevel

_ERR_NEGATIVE_INT = "Given value `{}` is not a non-negative int."

_OPTION_ARGUMENT_NAME: Dict[str, Union[Options, Dict]] = {
    "file": Options.FILE,
    "log": Options.LOG_LEVEL,
    "logfile": Options.LOG_FILE,
    "output": Options.OUTPUT,
    "encoding": Options.INPUT_ENCODING,
    "agents": Options.AGENT_LIST,
    "single_export": Options.SINGLE_AGENT_EXPORT,
    "memory_saving": Options.MEMORY_SAVING,
    "time": Options.TIME,
    "input_recovery": Options.INPUT_RECOVERY,
    "complex_column": Options.RESOLVE_COMPLEX_FIELD,
    "time_merging": {
        "name": Options.TIME_MERGING,
        "inner_elements": {
            "focal_point": MergingOptions.FOCAL_POINT,
            "steps_before": MergingOptions.STEPS_BEFORE,
            "steps_after": MergingOptions.STEPS_AFTER,
        },
    },
}


def add_file_argument(parser: ArgumentParser, default: Optional[Path], help_text: str) -> None:
    """
    Adds 'file' argument to the provided `parser` with the provided `help_text`.
    If a default is not specified, the argument is required (optional otherwise)

    Args:
        parser: to add the argument to
        default: optional, if it is a valid Path, it is added as default and the argument becomes optional
        help_text: to be displayed
    """
    if default is not None and isinstance(default, (Path, str)):
        parser.add_argument("-f", "--file", type=Path, required=False, default=default, help=help_text)
    else:
        parser.add_argument("-f", "--file", type=Path, required=True, help=help_text)


def add_select_agents_argument(parser: ArgumentParser, default: List[str]) -> None:
    """Adds optional repeatable string argument 'agent' to given `parser`"""
    help_text = "Provide list of agents to extract (default=None)"
    parser.add_argument("-a", "--agents", nargs="*", type=str, default=default, help=help_text)


def add_logfile_argument(parser: ArgumentParser, default: Path) -> None:
    """Adds optional argument 'logfile' to given `parser`"""
    help_text = "provide logging file (default=None)"
    parser.add_argument("-lf", "--logfile", type=Path, default=default, help=help_text)


def add_output_argument(parser: ArgumentParser, default_value, help_text: str) -> None:
    """Adds optional argument 'output' to given `parser` using the given `help_text` and `default_value`"""
    parser.add_argument("-o", "--output", type=Path, default=default_value, help=help_text)


def add_log_level_argument(parser: ArgumentParser, default_value: str) -> None:
    """Adds optional argument 'log' to given `parser`"""
    help_text = "choose logging level (default: {})".format(default_value)
    parser.add_argument(
        "-l",
        "--log",
        default=default_value,
        choices=[level.name for level in LogLevel if level not in [LogLevel.PRINT, LogLevel.WARN]],
        type=str.upper,
        help=help_text,
    )


def add_encoding_argument(parser: ArgumentParser, default_value: Optional[str], help_text: str) -> None:
    """Adds optional argument `enc` to given parser"""
    parser.add_argument("-enc", "--encoding", type=str, default=default_value, help=help_text)


def add_single_export_argument(parser: ArgumentParser, default_value: bool) -> None:
    """Adds optional repeatable string argument 'agent' to given `parser`"""
    help_text = "Enable export of single agents (default=False)"
    parser.add_argument(
        "-se",
        "--single-export",
        default=default_value,
        action="store_true",
        help=help_text,
    )


def add_memory_saving_argument(parser: ArgumentParser, default_value: bool) -> None:
    """Adds optional bool argument to given `parser` to enable memory saving mode"""
    help_text = "Reduces memory usage profile at the cost of runtime (default=False)"
    parser.add_argument(
        "-m",
        "--memory-saving",
        default=default_value,
        action="store_true",
        help=help_text,
    )


def add_resolve_complex_argument(parser: ArgumentParser, default_value: Union[ResolveOptions, str]):
    """Instructs given `parser` how to deal with complex field outputs"""
    default_value = default_value if isinstance(default_value, ResolveOptions) else ResolveOptions[default_value]
    help_text = f"How to deal with complex index columns? (default={default_value})"
    parser.add_argument(
        "-cc",
        "--complex-column",
        type=ResolveOptions.instantiate,
        default=default_value,
        choices=ResolveOptions,
        help=help_text,
    )


def add_time_argument(parser: ArgumentParser, default_value: Union[TimeOptions, str]) -> None:
    """Adds optional argument to given `parser` to define conversion of TimeSteps"""
    default_value = default_value if isinstance(default_value, TimeOptions) else TimeOptions[default_value]
    help_text = "Apply conversion of time steps to given format (default=UTC)"
    parser.add_argument(
        "-t",
        "--time",
        type=TimeOptions.instantiate,
        default=default_value,
        choices=TimeOptions,
        help=help_text,
    )


def add_merge_time_parser(parser: ArgumentParser, defaults: Optional[Dict[MergingOptions, int]]) -> None:
    """
    Adds subparser for merging of TimeSteps to given `parser`
    If at least one valid time merging option is specified in given defaults, calling the subparser becomes mandatory
    """
    defaults = defaults if (defaults is not None) and (isinstance(defaults, dict)) else {}
    if any([option in defaults.keys() for option in MergingOptions]):
        subparser = parser.add_subparsers(dest="time_merging", required=True, help="Optional merging of TimeSteps")
    else:
        subparser = parser.add_subparsers(dest="time_merging", required=False, help="Optional merging of TimeSteps")
    group_parser = subparser.add_parser("merge-times")
    add_focal_point_argument(group_parser, defaults.get(MergingOptions.FOCAL_POINT, None))
    add_steps_before_argument(group_parser, defaults.get(MergingOptions.STEPS_BEFORE, None))
    add_steps_after_argument(group_parser, defaults.get(MergingOptions.STEPS_AFTER, None))


def add_focal_point_argument(parser: ArgumentParser, default_value: Optional[int]) -> None:
    """Adds `focal-point` argument to given `parser`"""
    help_text = "TimeStep on which `steps_before` earlier and `steps_after` later TimeSteps are merged on"
    if default_value is not None:
        parser.add_argument("-fp", "--focal-point", required=False, type=int, help=help_text, default=default_value)
    else:
        parser.add_argument("-fp", "--focal-point", required=True, type=int, help=help_text)


def add_steps_before_argument(parser: ArgumentParser, default_value: Optional[int]) -> None:
    """Adds `steps-before` argument to given `parser`"""
    help_text = "Range of TimeSteps before the `focal-point` they get merged to"
    if default_value is not None:
        parser.add_argument(
            "-sb", "--steps-before", required=False, type=_non_negative_int, help=help_text, default=default_value
        )
    else:
        parser.add_argument("-sb", "--steps-before", required=True, type=_non_negative_int, help=help_text)


def _non_negative_int(value: Any) -> int:
    """
    Casts a given ´value` to int and checks it for non-negativity

    Args:
        value: to check and parse

    Returns:
        `value` parsed to int if it is a non-negative integer

    Raises:
        TypeError: if `value` is None
        ValueError: if `value` cannot be parsed to int
        argparse.ArgumentTypeError: if `value` is a negative int

    """
    value = int(value)
    if value < 0:
        raise ArgumentTypeError(_ERR_NEGATIVE_INT.format(value))
    return value


def add_steps_after_argument(parser: ArgumentParser, default_value: Optional[int]) -> None:
    """Adds `steps-after` argument to given `parser`"""
    help_text = "Range of TimeSteps after the `focal-point` they get merged to"
    if default_value is not None:
        parser.add_argument(
            "-sa", "--steps-after", required=False, type=_non_negative_int, help=help_text, default=default_value
        )
    else:
        parser.add_argument("-sa", "--steps-after", required=True, type=_non_negative_int, help=help_text)


def add_inputs_recovery_argument(parser: ArgumentParser, default: bool) -> None:
    """Adds optional bool argument to given `parser` to recover inputs"""
    help_text = "If --(no-)input-recovery is specified, (no) inputs will be recovered"
    parser.add_argument(
        "--input-recovery",
        action=BooleanOptionalAction,
        default=default,
        help=help_text,
    )


def update_default_config(config: Optional[dict], default: dict) -> dict:
    """Returns `default` config with updated fields received from `config`"""
    result = copy.deepcopy(default)
    if config:
        for name, option in config.items():
            result[name] = option
    return result


def map_namespace_to_options_dict(parsed: Namespace) -> Dict[Options, Any]:
    """
    Maps given parsing results to their corresponding configuration option

    Args:
        parsed: result of a parsing

    Returns:
        Map of each parsed argument to their configuration option
    """
    return _map_namespace_to_options(parsed, _OPTION_ARGUMENT_NAME)


def _map_namespace_to_options(parsed: Namespace, names_to_options: Dict[str, Enum]) -> Dict[Options, Any]:
    """
    Maps given parsing results to their corresponding configuration option; elements that cannot be mapped are ignored.
    If a configuration option has inner elements, these well be also read and added as inner dictionary.

    Args:
        parsed: result of a parsing
        names_to_options: dict to search for configuration option specifications

    Returns:
         Map parsed arguments to their configuration option if they exist in the given `names_to_options` dict
    """
    config = {}
    for name, value in vars(parsed).items():
        option = names_to_options.get(name, None)
        if option:
            if isinstance(option, dict):
                inner_element_map = option["inner_elements"]
                option = option["name"]
                value = _map_namespace_to_options(parsed, inner_element_map)
            config[option] = value
    return config

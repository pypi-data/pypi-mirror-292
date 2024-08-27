# SPDX-FileCopyrightText: 2023 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import math
from typing import Dict, Optional

import pandas as pd

from fameio.source.cli.options import TimeOptions, MergingOptions
from fameio.source.logs import log_error_and_raise, log
from fameio.source.time import ConversionException, FameTime

_ERR_UNIMPLEMENTED = "Time conversion mode '{}' not implemented."


def apply_time_merging(data: Dict[Optional[str], pd.DataFrame], config: Optional[Dict[MergingOptions, int]]) -> None:
    """
    Applies merging of TimeSteps inplace for given `data`

    Args:
        data: one or multiple DataFrames of time series; column `TimeStep` might be modified
        config: dict of MergingOptions defining how to merge the TimeSteps

    Returns:
        Nothing - data is modified inplace
    """
    if config:
        log().debug(f"Grouping TimeSteps...")
        offset = config[MergingOptions.STEPS_BEFORE]
        period = config[MergingOptions.STEPS_AFTER] + config[MergingOptions.STEPS_BEFORE] + 1
        first_positive_focal_point = config[MergingOptions.FOCAL_POINT] % period
        for key in data.keys():
            df = data[key]
            index_columns = df.index.names
            df.reset_index(inplace=True)
            df["TimeStep"] = df["TimeStep"].apply(lambda t: merge_time(t, first_positive_focal_point, offset, period))
            data[key] = df.groupby(by=index_columns).sum()


def merge_time(time_step: int, focal_time: int, offset: int, period: int) -> int:
    """
    Returns `time_step` rounded to its corresponding focal point

    Args:
        time_step: TimeStep to round
        focal_time: First positive focal point
        offset: Range of TimeSteps left of the focal point
        period: Total range of TimeSteps belonging to the focal point

    Returns:
        Corresponding focal point
    """
    return math.floor((time_step + offset - focal_time) / period) * period + focal_time


def apply_time_option(data: Dict[Optional[str], pd.DataFrame], mode: TimeOptions) -> None:
    """
    Applies time option based on given `mode` inplace of given `data`

    Args:
        data: one or multiple DataFrames of time series; column `TimeStep` might be modified (depending on mode)
        mode: name of time conversion mode (derived from Enum)

    Returns:
        Nothing - data is modified inplace
    """
    if mode == TimeOptions.INT:
        log().debug("No time conversion...")
    elif mode == TimeOptions.UTC:
        _convert_time_index(data, "%Y-%m-%d %H:%M:%S")
    elif mode == TimeOptions.FAME:
        _convert_time_index(data, "%Y-%m-%d_%H:%M:%S")
    else:
        log_error_and_raise(ConversionException(_ERR_UNIMPLEMENTED.format(mode)))


def _convert_time_index(data: Dict[Optional[str], pd.DataFrame], datetime_format: str) -> None:
    """
    Inplace replacement of `TimeStep` column in MultiIndex of each item of `data` from FAME's time steps` to DateTime
    in given `date_format`

    Args:
        data: one or multiple DataFrames of time series; column `TimeStep` will be modified
        datetime_format: used for the conversion

    Returns:
        Nothing - data is modified inplace
    """
    log().debug(f"Converting TimeStep to format '{datetime_format}'...")
    for _, df in data.items():
        index_columns = df.index.names
        df.reset_index(inplace=True)
        df["TimeStep"] = df["TimeStep"].apply(lambda t: FameTime.convert_fame_time_step_to_datetime(t, datetime_format))
        df.set_index(keys=index_columns, inplace=True)

# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import Dict

import yaml

from fameio.source.logs import log

ERR_WRITE_EXCEPTION = "Failed to save dictionary to YAML file `{}`"
INFO_DESTINATION = "Saving scenario to file at {}"


def data_to_yaml_file(data: Dict, file_path: Path) -> None:
    """
    Save the given data to a YAML file at given path

    Args:
        data: to be saved to yaml file
        file_path: at which the file will be created
    """
    log().info(INFO_DESTINATION.format(file_path))
    try:
        with open(file_path, "w") as f:
            yaml.dump(data, f, sort_keys=False)
    except Exception as e:
        raise RuntimeError(ERR_WRITE_EXCEPTION.format(file_path)) from e

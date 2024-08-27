#!/usr/bin/env python
import sys
from pathlib import Path

import pandas as pd

from fameio.source.cli.convert_results import handle_args, CLI_DEFAULTS as DEFAULT_CONFIG
from fameio.source.cli.options import Options
from fameio.source.cli.parser import update_default_config
from fameio.source.logs import log_and_raise_critical, fameio_logger, log
from fameio.source.results.agent_type import AgentTypeLog
from fameio.source.results.conversion import apply_time_option, apply_time_merging
from fameio.source.results.csv_writer import CsvWriter
from fameio.source.results.data_transformer import DataTransformer, INDEX
from fameio.source.results.input_dao import InputDao
from fameio.source.results.output_dao import OutputDAO
from fameio.source.results.reader import Reader
from fameio.source.results.yaml_writer import data_to_yaml_file

ERR_MEMORY_ERROR = "Out of memory. Try using `-m` or `--memory-saving` option."
ERR_MEMORY_SEVERE = "Out of memory despite memory-saving mode. Reduce output interval in `FAME-Core` and rerun model."


def run(config: dict = None) -> None:
    """Reads file in protobuf format for configures FILE and extracts its content to .csv file(s)"""
    config = update_default_config(config, DEFAULT_CONFIG)
    fameio_logger(log_level_name=config[Options.LOG_LEVEL], file_name=config[Options.LOG_FILE])

    file_path = config[Options.FILE]
    output_writer = CsvWriter(config[Options.OUTPUT], Path(file_path), config[Options.SINGLE_AGENT_EXPORT])
    file_stream = open(Path(file_path), "rb")

    if config[Options.MEMORY_SAVING]:
        log().info("Memory saving mode enabled: Disable on conversion of small files for performance improvements.")

    log().info("Reading and extracting data...")
    reader = Reader.get_reader(file=file_stream, read_single=config[Options.MEMORY_SAVING])
    agent_type_log = AgentTypeLog(requested_agents=config[Options.AGENT_LIST])
    data_transformer = DataTransformer.build(config[Options.RESOLVE_COMPLEX_FIELD])
    try:
        input_dao = InputDao()
        while data_storages := reader.read():
            if config[Options.INPUT_RECOVERY]:
                input_dao.store_inputs(data_storages)
            output = OutputDAO(data_storages, agent_type_log)
            for agent_name in output.get_sorted_agents_to_extract():
                log().debug(f"Extracting data for {agent_name}...")
                data_frames = output.get_agent_data(agent_name, data_transformer)
                if not config[Options.MEMORY_SAVING]:
                    apply_time_merging(data_frames, config[Options.TIME_MERGING])
                    apply_time_option(data_frames, config[Options.TIME])
                log().debug(f"Writing data for {agent_name}...")
                output_writer.write_to_files(agent_name, data_frames)

        if config[Options.INPUT_RECOVERY]:
            log().info("Recovering inputs...")
            timeseries, scenario = input_dao.recover_inputs()
            series_writer = CsvWriter(Path(config[Options.OUTPUT], "./recovered"), Path("./"), False)
            series_writer.write_time_series_to_disk(timeseries)
            data_to_yaml_file(scenario.to_dict(), Path(config[Options.OUTPUT], "./recovered/scenario.yaml"))

        if config[Options.MEMORY_SAVING]:
            written_files = output_writer.pop_all_file_paths()
            for agent_name, file_path in written_files.items():
                parsed_data = {None: pd.read_csv(file_path, sep=";", index_col=INDEX)}
                apply_time_merging(parsed_data, config[Options.TIME_MERGING])
                apply_time_option(parsed_data, config[Options.TIME])
                output_writer.write_to_files(agent_name, parsed_data)

        log().info("Data conversion completed.")
    except MemoryError:
        log_and_raise_critical(ERR_MEMORY_SEVERE if Options.MEMORY_SAVING else ERR_MEMORY_ERROR)

    file_stream.close()
    if not agent_type_log.has_any_agent_type():
        log().error("Provided file did not contain any output data.")


if __name__ == "__main__":
    run_config = handle_args(sys.argv[1:])
    run(run_config)

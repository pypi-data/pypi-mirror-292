import os
from pathlib import Path
import re
import shutil


def default_number_of_workers() -> int:
    cpu_count = os.cpu_count()
    if cpu_count is None:
        return 1
    return cpu_count


def gather_files_in_directory(directory: Path, regex: re.Pattern) -> list[Path]:
    # Gather all files in the directory, recursively too, so long as they match the regex
    files = list()
    for file in directory.rglob("*"):
        if regex.match(file.name):
            files.append(file)

    return files


def gather_all_files(directories: list[Path], regex: re.Pattern) -> list[Path]:
    files = list()

    for directory in directories:
        files.extend(gather_files_in_directory(directory, regex))

    return files


def get_log_paths_for_file(file: Path) -> tuple[Path, Path, Path]:
    # We store log files in a hidden directory next to the tests in that directory
    name = file.stem

    directory = file.parent
    log_directory = directory / ".logs"

    log_stdout = log_directory / f"{name}.stdout.log"
    log_stderr = log_directory / f"{name}.stderr.log"

    return (log_directory, log_stdout, log_stderr)

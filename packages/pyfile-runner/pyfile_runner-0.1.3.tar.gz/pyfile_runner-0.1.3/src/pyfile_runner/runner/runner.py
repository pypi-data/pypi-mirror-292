from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re

from pyfile_runner.runner.event import Callbacks, Event, FilesGatheredEvent, FinishedEvent, fire_event
from pyfile_runner.runner.util import default_number_of_workers, gather_all_files
from pyfile_runner.runner.worker import worker, WorkerConfig

DEFAULT_FILE_REGEX: re.Pattern = re.compile(r".*\.py")


class PyfileRunner():
    number_of_workers: int = default_number_of_workers()

    file_regex: re.Pattern = DEFAULT_FILE_REGEX
    directories: list[Path] = []

    on_event_callbacks: Callbacks = []

    worker_config: WorkerConfig | None = None

    def set_number_of_workers(self, number_of_workers: int) -> None:
        self.number_of_workers = number_of_workers

    def set_file_regex(self, regex: re.Pattern | str) -> None:
        if isinstance(regex, str):
            self.file_regex = re.compile(regex)
        else:
            self.file_regex = regex

    def add_directory(self, directory: Path | str) -> None:
        directory_path = Path(directory)

        if not directory_path.exists():
            raise ValueError(f"Path: {directory} does not exist")

        if not directory_path.is_dir():
            raise ValueError(f"Path: {directory} is not a directory")

        self.directories.append(directory_path)

    def add_on_event_callback(self, callback: Callable[[Event], None]) -> None:
        self.on_event_callbacks.append(callback)

    def set_worker_config(self, worker_config: WorkerConfig) -> None:
        self.worker_config = worker_config

    def run(self) -> None:
        files = gather_all_files(self.directories, self.file_regex)
        fire_event(self.on_event_callbacks, FilesGatheredEvent(files))

        pool = ThreadPoolExecutor(max_workers=self.number_of_workers)

        for file in files:
            pool.submit(worker, self.on_event_callbacks, file, self.worker_config)

        pool.shutdown()
        
        fire_event(self.on_event_callbacks, FinishedEvent())

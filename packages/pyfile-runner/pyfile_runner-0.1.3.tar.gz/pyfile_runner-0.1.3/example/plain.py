from pathlib import Path

from loguru import logger
from pyfile_runner.runner.event import Event, FileCompletedEvent, FileStartedEvent, FilesGatheredEvent, FinishedEvent
from pyfile_runner.runner.runner import PyfileRunner
from pyfile_runner.runner.worker import WorkerConfig


def on_event(event: Event) -> None:
    match event:
        case FilesGatheredEvent():
            logger.info(f"Gathered {len(event.files)} files")
        case FileStartedEvent():
            logger.info(f"Started file: {event.file}")
        case FileCompletedEvent():
            if event.success:
                logger.success(f"File: {event.file} succeeded")
            else:
                logger.error(f"File: {event.file} failed")
        case FinishedEvent():
            logger.info("All done!")


if __name__ == '__main__':
    # root = Path(os.path.dirname(os.path.realpath(__file__)))
    root = Path("example")

    runner = PyfileRunner()
    runner.set_number_of_workers(2)
    runner.set_worker_config(WorkerConfig().set_extend_env({"HELLO": "WORLD"}))
    runner.add_directory(root / 'files_a')
    runner.add_directory(root / 'files_b')
    runner.add_on_event_callback(on_event)
    runner.run()

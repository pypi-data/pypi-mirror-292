from collections.abc import Callable
import os
from pathlib import Path
import subprocess

from pyfile_runner.runner.event import Event, FileCompletedEvent, FileStartedEvent, fire_event
from pyfile_runner.runner.util import get_log_paths_for_file


def worker(on_event_callback: Callable[[Event], None] | None, file: Path) -> None:
    fire_event(on_event_callback, FileStartedEvent(file))

    (directory, log_path_stdout, log_path_stderr) = get_log_paths_for_file(file)
    
    # Ensure log directory exists, and old log files are cleaned up
    os.makedirs(directory, exist_ok=True)
    if os.path.exists(log_path_stdout):
        os.remove(log_path_stdout)
    if os.path.exists(log_path_stderr):
        os.remove(log_path_stderr)

    success = True

    with open(log_path_stdout, "w") as stdout_file, open(log_path_stderr, "w") as stderr_file:
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            subprocess.run(
                ["python", file],
                stdout=stdout_file,
                stderr=stderr_file,
                check=True,
                # TODO: allow setting a timeout
                env=env,
            )
        except subprocess.CalledProcessError:
            success = False
        except subprocess.TimeoutExpired:
            success = False

    fire_event(on_event_callback, FileCompletedEvent(file, success))
import os
from pathlib import Path
import subprocess

from pyfile_runner.runner.event import Callbacks, FileCompletedEvent, FileStartedEvent, fire_event
from pyfile_runner.runner.util import get_log_paths_for_file


class WorkerConfig:
    extend_env: dict[str, str] | None = None
    """Extend the environment variables for the worker process, the os.environ will be updated using env.update(extend_env)"""

    def set_extend_env(self, extend_env: dict[str, str]) -> "WorkerConfig":
        self.extend_env = extend_env
        return self


def worker(on_event_callbacks: Callbacks, file: Path, worker_config: WorkerConfig | None = None) -> None:
    fire_event(on_event_callbacks, FileStartedEvent(file))

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
            if worker_config and worker_config.extend_env:
                env.update(worker_config.extend_env)

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

    fire_event(on_event_callbacks, FileCompletedEvent(file, success))
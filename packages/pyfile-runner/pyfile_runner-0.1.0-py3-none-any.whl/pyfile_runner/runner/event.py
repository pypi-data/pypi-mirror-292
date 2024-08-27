from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Literal


class EventType(str, Enum):
    FILES_GATHERED = "FILES_GATHERED"
    FILE_STARTED = "FILE_STARTED"
    FILE_COMPLETED = "FILE_COMPLETED"
    FINISHED = "FINISHED"


class FilesGatheredEvent():
    type = Literal[EventType.FILES_GATHERED]
    files: list[Path]

    def __init__(self, files: list[Path]) -> None:
        self.files = files


class FileStartedEvent():
    type = Literal[EventType.FILE_STARTED]
    file: Path

    def __init__(self, file: Path) -> None:
        self.file = file


class FileCompletedEvent():
    type = Literal[EventType.FILE_COMPLETED]
    file: Path
    success: bool

    def __init__(self, file: Path, success: bool) -> None:
        self.file = file
        self.success = success


class FinishedEvent():
    type = Literal[EventType.FINISHED]


Event = FilesGatheredEvent | FileStartedEvent | FileCompletedEvent  | FinishedEvent


def fire_event(optional_callback: Callable[[Event], None] | None, event: Event) -> None:
    if optional_callback:
        optional_callback(event)
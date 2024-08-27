from pathlib import Path

from textual.message import Message


class FilesGathered(Message):
    files: list[Path]

    def __init__(self, files: list[Path]) -> None:
        super().__init__()
        self.files = files


class FileStarted(Message):
    file: Path

    def __init__(self, file: Path) -> None:
        super().__init__()
        self.file = file


class FileCompleted(Message):
    file: Path
    success: bool

    def __init__(self, file: Path, success: bool) -> None:
        super().__init__()
        self.file = file
        self.success = success


class FileSelected(Message):
    file: Path 

    def __init__(self, file: Path) -> None:
        super().__init__()
        self.file = file


class Finished(Message):
    pass
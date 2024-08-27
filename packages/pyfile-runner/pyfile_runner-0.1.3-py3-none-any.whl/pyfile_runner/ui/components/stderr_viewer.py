from collections.abc import Iterable
from pathlib import Path
from textual.containers import ScrollableContainer
from textual.widget import Widget
from textual.widgets import RichLog

from pyfile_runner.runner.util import get_log_paths_for_file


class StderrViewer(ScrollableContainer):
    def compose(self) -> Iterable[Widget]:
        yield RichLog()

    def load_file_output(self, file: Path) -> None:
        (_, _, log_path_stderr) = get_log_paths_for_file(file)

        # TODO: file polling
        with open(log_path_stderr, "r") as log_stderr:
            display = self.query_one(RichLog)
            display.clear()
            display.write("\n".join(log_stderr.readlines()))
from collections.abc import Iterable
from pathlib import Path
from textual.containers import ScrollableContainer
from textual.widget import Widget
from textual.widgets import TabbedContent

from pyfile_runner.ui.components.stderr_viewer import StderrViewer
from pyfile_runner.ui.components.stdout_viewer import StdoutViewer


class OutputViewer(ScrollableContainer, can_focus=False):
    BORDER_TITLE = "Output"

    def compose(self) -> Iterable[Widget]:
        with TabbedContent("stdout", "[red]stderr"):
            self.stdout_viewer = StdoutViewer()
            yield self.stdout_viewer
            self.stderr_viewer = StderrViewer()
            yield self.stderr_viewer

    def load_file_output(self, file: Path) -> None:
        self.stdout_viewer.load_file_output(file)
        self.stderr_viewer.load_file_output(file)
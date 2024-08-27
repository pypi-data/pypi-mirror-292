from collections.abc import Iterable
from datetime import datetime
from rich.style import Style
from rich.text import Text
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widget import Widget
from textual.widgets import Label, LoadingIndicator, ProgressBar, RichLog, Rule, Static

from pyfile_runner.ui.messages import FileCompleted, FileStarted, FilesGathered, Finished


class GatheringFiles(Static):
    def compose(self) -> Iterable[Widget]:
        with Vertical():
            yield LoadingIndicator()


class Bar(Widget, can_focus=False):
    pass

class CountOfTotal(Label):
    pass

class FilesProgressBar(Widget):
    DEFAULT_CSS = """
    FilesProgressBar {
        # padding-left: 2;
        # padding-right: 2;
        height: 1;
    }
    """

    def compose(self) -> Iterable[Widget]:
        with Horizontal():
            yield Bar()
            yield CountOfTotal()

        # with Horizontal():
        #     self.bar_queued = Rule(line_style="thick")
        #     self.bar_queued.styles.width = "60%"
        #     self.bar_queued.styles.color = "gray"
        #     yield self.bar_queued
        #     self.bar_started = Rule(line_style="thick")
        #     self.bar_started.styles.width = "10%"
        #     self.bar_started.styles.color = "yellow"
        #     yield self.bar_started
        #     self.bar_success = Rule(line_style="thick")
        #     self.bar_success.styles.width = "10%"
        #     self.bar_success.styles.color = "green"
        #     yield self.bar_success
        #     self.bar_failed = Rule(line_style="thick")
        #     self.bar_failed.styles.width = "20%"
        #     self.bar_failed.styles.color = "red"
        #     yield self.bar_failed


class FilesProgressContainer(ScrollableContainer, can_focus=False):
    BORDER_TITLE = "Progress Log"

    def compose(self) -> Iterable[Widget]:
        yield GatheringFiles()

    def handle_files_gathered(self, message: FilesGathered) -> None:
        self.query_one(GatheringFiles).remove()

        # self.mount(FilesProgressBar())
        self.mount(RichLog())

    def handle_file_started(self, message: FileStarted) -> None:
        text = Text(f"[{timestamp()}] Started: {message.file}", Style(color="yellow"))
        self.query_one(RichLog).write(text)

    def handle_file_completed(self, message: FileCompleted) -> None:
        text = Text(f"[{timestamp()}] {"Succeeded" if message.success else "Failed"}: {message.file}", Style(color="green" if message.success else "red"))
        self.query_one(RichLog).write(text)

    def handle_finished(self, message: Finished) -> None:
        text = Text(f"[{timestamp()}] All done!", Style(color="blue"))
        self.query_one(RichLog).write(text)

        
def timestamp() -> datetime:
    time = datetime.now().replace(microsecond=0)
    return time
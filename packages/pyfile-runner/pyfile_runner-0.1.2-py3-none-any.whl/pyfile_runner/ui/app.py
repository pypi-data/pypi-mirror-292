from collections.abc import Iterable
from pathlib import Path
from textual import on
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Footer, RichLog

from pyfile_runner.runner.event import Event, FileCompletedEvent, FileStartedEvent, FilesGatheredEvent, FinishedEvent
from pyfile_runner.runner.runner import PyfileRunner
from pyfile_runner.ui.components.files_bar import FilesBar
from pyfile_runner.ui.components.files_progress import FilesProgressContainer
from pyfile_runner.ui.components.files_tree import FilesTreeContainer
from pyfile_runner.ui.components.output_viewer import OutputViewer
from pyfile_runner.ui.messages import FileCompleted, FileSelected, FileStarted, FilesGathered, Finished

class PyfileRunnerUI(App):
    CSS_PATH = "app.tcss"

    BINDINGS = [
        # ("n", "next", "Next"),
        # ("p", "previous", "Previous"),
    ]

    runner: PyfileRunner

    root: Path | None = None

    def __init__(self, runner: PyfileRunner):
        super().__init__()

        self.runner = runner
        self.runner.add_on_event_callback(self.on_runner_event)


    def compose(self) -> Iterable[Widget]:
        with Horizontal():
            with FilesBar():
                yield FilesTreeContainer(self.root)
                # yield FilesProgressContainer()
            yield OutputViewer()
        yield FilesProgressContainer()
        yield Footer()

        self.run_worker(self.start_runner, thread=True)


    def set_root(self, root: str | Path) -> None:
        self.root = Path(root)
        if not self.root.is_dir(): 
            raise ValueError(f"root: {root} is not a directory")

    def start_runner(self) -> None:
        self.runner.run()

    @on(FilesGathered)
    def handle_files_gathered(self, message: FilesGathered) -> None:
        self.query_one(FilesTreeContainer).handle_files_gathered(message)
        self.query_one(FilesProgressContainer).handle_files_gathered(message)

    @on(FileStarted)
    def handle_file_started(self, message: FileStarted) -> None:
        self.query_one(FilesTreeContainer).handle_file_started(message)
        self.query_one(FilesProgressContainer).handle_file_started(message)

    @on(FileCompleted)
    def handle_file_completed(self, message: FileCompleted) -> None:
        self.query_one(FilesTreeContainer).handle_file_completed(message)
        self.query_one(FilesProgressContainer).handle_file_completed(message)

    @on(FileSelected)
    def handle_file_selected(self, message: FileSelected) -> None:
        self.query_one(OutputViewer).load_file_output(message.file)

    @on(Finished)
    def handle_finished(self, message: Finished) -> None:
        self.query_one(FilesProgressContainer).handle_finished(message)

    def on_runner_event(self, event: Event) -> None:
        match event:
            case FilesGatheredEvent():
                self.post_message(FilesGathered(event.files))
            case FileStartedEvent():
                self.post_message(FileStarted(event.file))
            case FileCompletedEvent():
                self.post_message(FileCompleted(event.file, event.success))
            case FinishedEvent():
                self.post_message(Finished())
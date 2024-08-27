from collections.abc import Iterable
from enum import Enum
from pathlib import Path
from rich.color import Color
from rich.style import Style
from rich.text import Text
from textual import on
from textual.containers import ScrollableContainer, Vertical
from textual.events import Click
from textual.widget import Widget
from textual.widgets import LoadingIndicator, Static, Tree
from textual.widgets.tree import TreeNode

from pyfile_runner.ui.messages import FileCompleted, FileSelected, FileStarted, FilesGathered


class GatheringFiles(Static):
    def compose(self) -> Iterable[Widget]:
        with Vertical():
            yield LoadingIndicator()


class State(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Data():
    ref: str
    file: Path
    is_leaf: bool
    state = State.PENDING

    def __init__(self, ref: str, file: Path, is_leaf: bool = False) -> None:
        self.ref = ref
        self.file = file
        self.is_leaf = is_leaf
    

class FilesTree(Tree[Data]):
    DEFAULT_CSS = """
    FilesTree {
        background: red 0%;
    }

    FilesTree > .tree--cursor {
        background: grey;
    }

    FilesTree:focus > .tree--cursor {
        background: grey;
    }
    """

    def __init__(self) -> None:
        super().__init__(label="/")

    def render_label(self, node: TreeNode[Data], base_style: Style, style: Style) -> Text:
        if not node.data:
            return super().render_label(node, base_style, style)

        if not node.data.is_leaf:
            node_label = node._label.copy()

            # style = Style(color=Color.from_rgb(112, 118, 144), bgcolor=style.bgcolor)
            style = Style(color="white", bgcolor=style.bgcolor)
            node_label.stylize(style)

            if node._allow_expand:
                prefix = (
                    "▼ " if node.is_expanded else "▶ ",
                    base_style,
                )
            else:
                prefix = ("", base_style)

            text = Text.assemble(prefix, node_label)
            return text
        else:
            node_label = node._label.copy()

            match node.data.state:
                case State.STARTED:
                    style = Style(color="yellow", bgcolor=style.bgcolor)
                case State.SUCCEEDED:
                    style = Style(color="green", bgcolor=style.bgcolor)
                case State.FAILED:
                    style = Style(color="red", bgcolor=style.bgcolor)

            node_label.stylize(style)

            text = Text.assemble(node_label)
            return text

    @on(Tree.NodeSelected)
    def handle_node_selected(self, message: Tree.NodeSelected[Data]) -> None:
      node = message.node
      if node.data and node.data.is_leaf:
          self.post_message(FileSelected(node.data.file))
          


class FilesTreeContainer(ScrollableContainer, can_focus=False):
    BORDER_TITLE = "Files"

    files_tree: FilesTree | None = None
    tree_refs: dict[str, TreeNode[Data]] | None = None

    root: Path | None  # TODO

    def __init__(self, root: Path | None = None) -> None:
        super().__init__()
        self.root = root

    def compose(self) -> Iterable[Widget]:
        yield GatheringFiles()

    def handle_files_gathered(self, message: FilesGathered) -> None:
        self.query_one(GatheringFiles).remove()

        tree = FilesTree()
        tree.root.expand()

        tree_refs = {}

        for file in message.files:
            for (i, part) in enumerate(file.parts):
                ref = "/".join(file.parts[:i+1])
                if ref in tree_refs:
                    continue

                if i == 0:
                    tree_node = tree.root.add(part, expand=True, data=Data(ref, file))
                    tree_refs[ref] = tree_node
                else:
                    parent_ref = "/".join(file.parts[:i])
                    parent_node = tree_refs[parent_ref]

                    if i == len(file.parts) - 1:
                        tree_leaf = parent_node.add_leaf(part, data=Data(ref, file, is_leaf=True))
                        tree_refs[ref] = tree_leaf
                    else:
                        tree_node = parent_node.add(part, expand=True, data=Data(ref, file))
                        tree_refs[ref] = tree_node

        self.files_tree = tree
        self.tree_refs = tree_refs

        self.mount(tree)

    def handle_file_started(self, message: FileStarted) -> None:
        if not self.tree_refs:
            raise ValueError("tree_refs is None")

        ref = "/".join(message.file.parts)
        
        data = self.tree_refs[ref].data
        if not data:
            raise ValueError(f"data for node: {ref} is None")
        
        data.state = State.STARTED

        if not self.files_tree:
            raise ValueError("files_tree is None")
        
        self.files_tree.root.refresh()
        self.files_tree.refresh()

    def handle_file_completed(self, message: FileCompleted) -> None:
        if not self.tree_refs:
            raise ValueError("tree_refs is None")

        ref = "/".join(message.file.parts)
        
        data = self.tree_refs[ref].data
        if not data:
            raise ValueError(f"data for node: {ref} is None")
        
        data.state = State.SUCCEEDED if message.success else State.FAILED
        
        if not self.files_tree:
            raise ValueError("files_tree is None")
        
        self.files_tree.root.refresh()
        self.files_tree.refresh()
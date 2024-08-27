import os
from pathlib import Path
from pyfile_runner.runner.runner import PyfileRunner
from pyfile_runner.ui.app import PyfileRunnerUI


if __name__ == '__main__':
    root = Path("example")
    # root = Path(os.path.dirname(os.path.realpath(__file__)))

    runner = PyfileRunner()
    # runner.set_number_of_workers(16)
    runner.set_number_of_workers(2)
    runner.add_directory(root / 'files_a')
    runner.add_directory(root / 'files_b')

    ui = PyfileRunnerUI(runner=runner)
    ui.set_root(root)
    ui.run()

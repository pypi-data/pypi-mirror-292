# Pyfile Runner

Simple Python library to help run multiple Python files and view their output while running.

This "library" contains both a runner, and a TUI which uses that runner to display the output nicely in a terminal.

## Example

```python

# Assuming you have some files you want to run in a directory named "tests"
if __name__ == '__main__':
    root = Path("tests")

    runner = PyfileRunner()
    runner.set_number_of_workers(4)  # Or remove this to use the available parallelism on your machine
    runner.add_directory(root)

    # Now you can either call `runner.run()` and use it for example in a CI where there is no interface needed.
    
    # Or you can wrap it in the TUI, to get nice output.
    ui = PyfileRunnerUI(runner=runner)
    ui.set_root(root)
    ui.run()
```

![screenshot](./.readme/screen.png)

#### Building and publishing

```
uvx --from build pyproject-build --installer uv
```

```
uvx twine upload dist/*
```
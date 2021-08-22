# `python-isolate`

[![CI](https://github.com/chowder/python-isolate/actions/workflows/ci.yml/badge.svg)](https://github.com/chowder/python-isolate/actions/workflows/ci.yml) ![wheels](https://img.shields.io/pypi/wheel/isolate)

A Python package to interface with [`isolate`](https://github.com/ioi/isolate) sandboxes.

## Example

`isolate` sandboxes are typically used in the following way:

- Run `isolate --init`, which initialises the sandbox, creates its working directory and prints its name to the standard output.Fails if the sandbox already existed.
- Populate the directory with the executable file of the program and its input files.
- Call `isolate --run` to run the program. A single line describing the status of the program is written to the standard error stream.
- Fetch the output of the program from the directory.
- Run `isolate --cleanup` to remove temporary files. Does nothing if the sandbox was already cleaned up.

The simplest example of this workflow in Python is as follows:

```python
from isolate import isolate

# Initialise the sandbox
with isolate() as workspace:
    # Populate the directory
    workspace.add_file('~/example.sh')
    # Run the program with arguments
    result = workspace.run(['/bin/bash', 'example.sh'])

# Sandbox is automatically cleaned up
```

## Distributions

- https://pypi.org/project/isolate/

## Requirements

- You need to have the [`isolate`](https://github.com/ioi/isolate) binary installed on your machine to use the package.

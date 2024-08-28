# Development setup

The following tools should be installed using the system package manager:

- black
- flake8
- flit
- hut
- isort
- python3-venv

Several project-related tasks are defined in `tasks.py`.
To run them, `yatte` itself must be installed in a virtualenv:

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install .

The package can then be reïnstalled in development mode,
along with the dependencies that can't be installed globally:

    $ yatte setup

Other project-related tasks can then be listed and run:

    $ yatte
    $ yatte fmt  # etc.

The code can be checked automatically when making a Git commit
by saving the following script as `.git/hook/pre-commit`
and making it executable with `chmod +x`:

    #!/bin/sh -e
    yatte check

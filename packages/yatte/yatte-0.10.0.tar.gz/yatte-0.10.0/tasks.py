import os
import sys

from yatte import task
from yatte.utils import run, runp


@task("setup")
def setup():
    "Set up development environment."
    try:
        venv = os.path.relpath(os.getenv("VIRTUAL_ENV"))
    except ValueError:
        sys.exit("ERROR: virtualenv is not activated")

    run(f"flit install -s --python {venv}/bin/python")


@task("lint")
def run_linters():
    """Run linters."""
    cmds = [
        "isort --check .",
        "black --check .",
        "flake8 .",
    ]
    runp(cmds)


@task("test")
def run_tests():
    """Run tests."""
    run("pytest -q .")


@task("check")
def check():
    """lint + test"""
    cmds = [
        "isort --check .",
        "black --check .",
        "flake8 .",
        "pytest -q .",
    ]
    runp(cmds)


@task("fmt")
def format():
    """Run formatters."""
    run("isort .")
    run("black .")


sys.path.insert(0, "docs")
import doctasks  # noqa: E402 F401


@task("upload")
def pypi():
    """Publish package to PyPI."""
    run("flit publish")


@task("clean")
def clean():
    """Remove build/test artefacts."""
    run("rm -rf .pytest_cache")
    run("rm -rf __pycache__ */__pycache__")
    run("rm -rf dist")
    run("rm -rf docs/_built")

"""Helper functions for use in writing tasks"""

import os
import shlex
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from logging import error


def stderr(s):
    """Print a string to stderr."""
    print(s, file=sys.stderr)


def run(cmd):
    """Run a shell command."""
    if isinstance(cmd, list):
        cmd = shlex.join(cmd)

    stderr(f"$ {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


def runp(cmds):
    """Run shell commands in parallel."""
    with ProcessPoolExecutor() as executor:
        retcodes = list(executor.map(_run, cmds))

    if any(retcodes):
        sys.exit(max(retcodes))


def _run(cmd):
    """Run a shell command and print its output upon completion."""
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    stderr(f"$ {cmd}")

    if p.stdout:
        print(p.stdout.rstrip())

    if p.stderr:
        stderr(p.stderr.rstrip())

    if p.returncode:
        error("Command %r returned non-zero exit status %d.", cmd, p.returncode)

    return p.returncode


def mkdir(d):
    """Create directory d if it doesn't already exist."""
    if not d.is_dir():
        run(["mkdir", "-p", str(d)])


def cp(src, dest):
    """Copy src to dest if dest doesn't already exist."""
    if not dest.is_file():
        mkdir(dest.parent)
        run(["cp", "-p", str(src), str(dest)])


def is_newer(f, than):
    """Return True if f exists and is newer than the second argument."""
    return f.is_file() and f.stat().st_mtime > than.stat().st_mtime


def assert_defined(names):
    """Check that the given names are defined as environment variables.

    Throws an AssertionError if any are undefined.
    """
    undefined = set(names) - set(os.environ)
    undefined_s = ", ".join(sorted(undefined))
    assert not undefined, f"Undefined environment variables: {undefined_s}"

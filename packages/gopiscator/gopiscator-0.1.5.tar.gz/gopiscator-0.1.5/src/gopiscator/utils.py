"""Various helper functions."""

from pathlib import Path


def read(rel_path: str) -> str:
    """Read file at the specified path."""
    here = Path(__file__).resolve().parent
    file_path = here / rel_path
    return file_path.read_text(encoding="utf-8")


def get_version(rel_path: str) -> str:
    """Extract version number from the specified file."""
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

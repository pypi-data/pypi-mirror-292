"""This file gets run when we call `python3 -m gopiscator`."""

import sys

from gopiscator.cli import main

if __name__ == "__main__":
    sys.exit(main())

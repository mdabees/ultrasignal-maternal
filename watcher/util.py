"""Small helpers shared by scripts and tests."""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def lower_priority():
    """Drop this process to below-normal priority so a laptop stays usable."""
    if sys.platform == "win32":
        import ctypes

        BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
        kernel32 = ctypes.windll.kernel32
        kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS)
    else:
        import os

        try:
            os.nice(5)
        except OSError:
            pass


def load_catalogue():
    with open(ROOT / "data" / "catalogue.json", encoding="utf-8") as handle:
        return json.load(handle)

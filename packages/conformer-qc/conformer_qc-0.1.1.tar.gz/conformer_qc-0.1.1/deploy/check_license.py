#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
"""
This helper script double checks all files (with the help of the licenseheaders package)
to make copyright information is included in each and every file as suggested 
by the Apache 2.0 License
"""

import logging
import subprocess
from copy import copy
from datetime import datetime

logger = logging.getLogger(__name__)

YEARS = "2018-" + str(datetime.now().year)
OWNERS = "Fragment Contributors"

EXCLUDED_FILES = ["public/*", "builds/*", ".vscode/*", ".gitlab/*"]

COMMAND = "licenseheaders"
ARGS = ["-t", "deploy/apache-2-min.tmpl", "-y", YEARS, "-o", OWNERS]

if EXCLUDED_FILES:
    EXCLUDED_ARGS = ["--exclude"] + EXCLUDED_FILES
else:
    EXCLUDED_ARGS = []

DRY_RUN_ARGS = ["-vvvv", "--dry"]

PROCESSING_STR = "Processing file "
INFO_STR = "Info for the file"


def quote_wrap(s):
    return '"' + s + '"'


def build_command(dry=False):
    """Build a runnable command as a string"""
    _OWNERS = quote_wrap(OWNERS)
    _YEARS = quote_wrap(YEARS)
    _EXCLUDED_ARGS = copy(EXCLUDED_ARGS)
    if _EXCLUDED_ARGS:
        for i in range(len(_EXCLUDED_ARGS) - 1):
            _EXCLUDED_ARGS[i + 1] = quote_wrap(_EXCLUDED_ARGS[i + 1])

    _ARGS = ["-t", "deploy/apache-2-min.tmpl", "-y", _YEARS, "-o", _OWNERS]

    if dry:
        _CMD = [COMMAND] + DRY_RUN_ARGS + _EXCLUDED_ARGS + _ARGS
    else:
        _CMD = [COMMAND] + _EXCLUDED_ARGS + _ARGS

    return " ".join(_CMD)


def main():
    sub_proc = subprocess.run(
        [COMMAND] + DRY_RUN_ARGS + EXCLUDED_ARGS + ARGS,
        capture_output=True,
        encoding="utf8",
    )
    if sub_proc.returncode != 0:
        logger.error(f"Could not run `{COMMAND}`")
        logger.error(sub_proc.stderr)
        return -1

    files = []
    current_file = None
    current_has_copyright = None

    for l in sub_proc.stderr.split("\n"):
        l = l.split(":")
        try:
            step_str = l[1]
            step_str = step_str.strip()
        except IndexError:
            continue

        # HANDLE PROCESSING
        if step_str.startswith(PROCESSING_STR):
            current_file = step_str
            _s = current_file.find(PROCESSING_STR)
            _e = current_file.rfind(" as ")
            current_file = current_file[(_s + len(PROCESSING_STR)) : _e]

        if step_str.startswith(INFO_STR):
            data = l[2].split(", ")
            data = [d.split("=") for d in data]
            data = {d[0]: d[1] for d in data}

            if data["haveLicense"] != "True" and data["yearsline"] == "None":
                current_has_copyright = False
            else:
                if data["yearsline"] == "None":
                    print("!!!!", current_file)
                current_has_copyright = True

            files.append((current_file, current_has_copyright))

    missing_header = list(filter(lambda x: not x[1], files))

    if missing_header:
        print("The project has files without a copyright header:")
        if len(missing_header) > 15:
            for f, s in missing_header[0:15]:
                print(" ", f)
            print(f"  ...and {len(missing_header) - 15} others")
        else:
            for f, s in missing_header[0:15]:
                print(" ", f)

        # Add quotes around the owners line
        print(f"Please run `{build_command(False)}` to fix this")
        return -2

    return 0


if __name__ == "__main__":
    exit(main())

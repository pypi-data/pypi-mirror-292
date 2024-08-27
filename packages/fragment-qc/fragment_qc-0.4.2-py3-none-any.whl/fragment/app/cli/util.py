#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import Any, List, Tuple

import click
from pydantic import ValidationError

from fragment.project import FragmentProject as Project

# from fragment.core.util import ValidationError, validate_slug

# Status Strings
ERROR = click.style("ERROR: ", fg="red")
WARNING = click.style("WARNING: ", fg="yellow")
INFO = click.style("INFO: ", fg="blue")
SUCCESS = click.style("Success! ", fg="green")


LOGGING_CHOICES = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


# Code for import strategy files
def loc_to_str(loc: Tuple[Any]):
    loc_str = ""
    last = None
    for l in loc:
        if isinstance(l, int):
            l_str = f"[{l}]"
        else:
            l_str = l

        if isinstance(l, str) and (last is not None):
            loc_str += "."
        loc_str += l_str
        last = l
    return loc_str


def import_strat_files(project: Project, strat_files: List[str]):
    for f in strat_files:
        click.echo(f"Adding `{f}`... ", nl=False)
        try:
            project.import_strategy(f)
        except ValidationError as ve:
            # TODO: Handle ctx variable
            click.echo("FAILED")
            addressed = set()
            for e in reversed(ve.errors()):
                loc = e["loc"]
                if loc in addressed:
                    continue
                else:
                    addressed.add(loc)
                loc_str = loc_to_str(loc)
                msg = e["msg"]
                click.echo(
                    "  " + click.style(f"{loc_str}", underline=True) + f": {msg}"
                )
                exit(-1)

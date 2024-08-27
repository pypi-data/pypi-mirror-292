#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime, timedelta
from sys import stdout

import click
import ray
import tqdm
from atomdriver.accessors import ACCESSOR_CACHE
from conformer.systems import System
from conformer_core.records import RecordStatus
from conformer_core.util import ind, summarize

from fragment.views import View, ViewRecord, ViewType


def stages_add_hook(stages):
    if not stages:
        return
    click.echo("Added new stages:")
    for s in stages:
        if s.meta.get("anonymous", False):
            click.echo(f"    Anonymous-{s.name[0:8]} ({s.__class__.__name__})")
        else:
            click.echo(f"    {s.name} ({s.__class__.__name__})")


def systems_add_hook(systems):
    if not systems:
        return
    click.echo("Added new systems:")
    for s in systems:
        click.echo(f"    {s.name}")


def calculations_add(name, calcs):
    if not calcs:
        return
    click.echo(f"Added calculations for `{name}`:")
    for c in calcs:
        click.echo(f"    {c.name}")

CHECK_TIME = datetime.now()
CHECK_INTERVAL = timedelta(seconds=30)


def calculation_status(project, calculations, force):
    global CHECK_TIME
    global CHECK_INTERVAL
    NOW = datetime.now()
    if force or (NOW > (CHECK_TIME + CHECK_INTERVAL)):
        CHECK_TIME = NOW
        with (project.PATH / ".status").open("w") as f:
            print("TIME:", NOW.isoformat(), file=f)
            print(file=f)

            print("DRIVER STATS:", file=f)
            for a in ACCESSOR_CACHE.values():
                print(
                    "  {}: {} ({}/{})".format(
                        a.accessor.driver.name,
                        a.accessor.num_active,
                        a.accessor.num_completed,
                        a.accessor.num_submitted,
                    ),
                    file=f,
                )
            print(file=f)

            if ray.ray.is_initialized():
                print(summarize("CLUSTER RESOURCES", ray.cluster_resources()), file=f)
                print(
                    summarize("AVAILABLE RESOURCES", ray.available_resources()), file=f
                )
            print(file=f)

            print("FAILED CALCULATIONS:", file=f)
            for c in calculations.values():
                if c.status == RecordStatus.FAILED:
                    print(f"  {c.name} ({c.status.name})", file=f)
            print(file=f)

            if force:
                print("FINAL", file=f)


def calc_start_hook(r):
    if r.status == RecordStatus.PENDING:
        click.echo(f"Starting '{r.name}'...")
    else:
        click.echo(f"Results for '{r.name}:'")


def calc_done_hook(r):
    click.echo()
    click.echo(r.summarize(level=1))


def calculation_failed(stage, args, value):
    click.echo("\b" * 3, nl=False)
    click.echo(" --> ", nl=False)
    click.echo(" FAILED")


def calculation_start_step(stage, args, value):
    if args:
        stage_name = stage.name + f"({', '.join((str(a) for a in args))})"
    else:
        stage_name = stage.name
    click.echo(ind(2, 1, f"running '{stage_name}'..."), nl=False)


def calculation_finish_step(stage, args, value):
    click.echo("\b" * 3, nl=False)
    if isinstance(value, View):
        num_nodes = (
            value.size(True) if value.type == ViewType.PRIMARY else value.size(False)
        )
        click.echo(
            f" --> View(name='{value.name}', type='{value.type.name}', fragments={num_nodes})"
        )
    elif isinstance(value, ViewRecord):
        if not stdout.isatty():
            click.echo(
                f" --> ViewRecord(view='{value.view.name}', fragments='{value.stage.name}')"
            )
    elif isinstance(value, System):
        click.echo(f" --> {value}")
    else:
        click.echo(" --> DONE")


def wrapped_driver_accessor_hook(driver, count):
    # Does this get disabled on non-tty? Manual says yes...
    prefix = ind(2, 1, f"running '{driver.driver.name}'... 🏃")
    return tqdm.tqdm(driver.as_completed(), desc=prefix, total=count, leave=True)

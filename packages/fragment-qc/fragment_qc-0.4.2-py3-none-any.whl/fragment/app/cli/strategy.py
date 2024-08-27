#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import List

import click
from conformer_core.registry import dump_yaml, load_yaml

from fragment.app.cli.util import import_strat_files

# from fragment.app.cli.util import INFO
# from fragment.conf.util import ConfigDoesNotExist
from fragment.project import FragmentProject as Project

# from fragment.systems.geometry_readers.util import SystemDoesNotExist


@click.group(help="Manage calculation strategies")
def strategy():
    pass


@strategy.command(help="Imports strategy elements from a yaml file")
@click.argument("strat_files", required=True, nargs=-1, type=click.Path(exists=True))
@click.pass_context
def add(ctx, strat_files):
    project: Project = ctx.obj["project"]
    import_strat_files(project, strat_files)


@strategy.command()
@click.option(
    "--with-class",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include each stage's class.",
)
@click.option(
    "--with-note", is_flag=True, default=False, help="Include each stage's note."
)
@click.option(
    "--show-anonymous",
    is_flag=True,
    default=False,
    help="Print the names for all anonymouse stages too.",
)
@click.pass_context
def list(ctx, with_class: bool, with_note: bool, show_anonymous: bool):
    project: Project = ctx.obj["project"]
    stages = project.get_stage_names()
    stages.sort(key=lambda a: a[2])  # Sort by type

    num_anons = 0
    for name, note, class_name, is_anon in stages:
        if is_anon and not show_anonymous:
            num_anons += 1
            continue
        stage = name
        if with_class:
            stage += " (" + class_name + ")"
        if with_note and note:
            stage += ": " + note
        click.echo(stage)

    if num_anons and not show_anonymous:
        click.echo()
        click.echo(f"+ {num_anons} anonymous stage" + ("s" if num_anons > 1 else ""))


@strategy.command(help="Edits the options for a stage")
@click.argument("stage_name", required=True, nargs=1, type=str)
@click.pass_context
def edit_options(ctx, stage_name):
    project: Project = ctx.obj["project"]

    stage = project.get_stage(stage_name)
    StageClass = stage.__class__
    OptionsClass = StageClass.Options
    print(StageClass)
    print(OptionsClass)

    click.echo("Editing Stage:")
    click.echo(stage.summarize(level=1))

    if click.confirm(
        "Changing the options for this stage may invalidate existing calculations. Would you like to continue?"
    ):
        edits = click.edit(dump_yaml(stage.opts.model_dump(), default_flow_style=False))
        if edits is None:
            click.echo("No changes made")
            return
        stage.opts = OptionsClass(**load_yaml(edits))
        project.update_stage(stage)
        click.echo("Update!")


@strategy.command(help="Print stage details")
@click.argument("stage_names", required=True, nargs=-1)
@click.pass_context
def info(ctx, stage_names: List[str]):
    project: Project = ctx.obj["project"]
    stages = project.get_stages(*stage_names)

    for name in stage_names:
        stage = stages[name]
        click.echo(stage.summarize())

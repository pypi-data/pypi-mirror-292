#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import os
import signal
from pathlib import Path

import click
from click.core import Context
from click.exceptions import ClickException
from conformer_core.util import summarize

import fragment.app.cli.hooks as hooks
from fragment.app.cli.calc import calc
from fragment.app.cli.strategy import strategy
from fragment.app.cli.system import system
from fragment.app.cli.util import import_strat_files

# from fragment.app.cli.util import ERROR, LOGGING_CHOICES, get_working_path
# from fragment.core.logging import configure_logger, teardown_logger
from fragment.project import FragmentProject as Project


def new_cli_project(
    base_path: Path, debug=False, cpus=None, use_ray=False, tmpdir=None
) -> Project:
    return Project(
        base_path=base_path,
        hooks={
            "calc_start": hooks.calc_start_hook,
            "calc_finish": hooks.calc_done_hook,
            "stages_add": hooks.stages_add_hook,
            "systems_add": hooks.systems_add_hook,
            "calculations_add": hooks.calculations_add,
            "calculation_status": hooks.calculation_status,
            "calculation_start_step": hooks.calculation_start_step,
            "calculation_finish_step": hooks.calculation_finish_step,
            "calculation_failed": hooks.calculation_failed,
            "wrap_driver_accessor": hooks.wrapped_driver_accessor_hook,
        },
        cpus=cpus,
        tmpdir=tmpdir,
        use_ray=use_ray,
        debug=debug,
    )


@click.group()
@click.option(
    "-p",
    "--project-folder",
    required=False,
    type=click.Path(resolve_path=True),
    help="Project path to write the database and I/O files",
)
@click.option(
    "-t",
    "--tmpdir",
    required=False,
    type=click.Path(resolve_path=True),
    help="Directory for DB storage while running calculations",
)
@click.option(
    "--db-file",
    required=False,
    type=str,
    default="fragment.db",
    help="Alternative database file.",
)
@click.option(
    "--debug", type=bool, default=False, is_flag=True, help="Run in debug mode"
)
@click.option(
    "--ray",
    "-r",
    type=bool,
    default=False,
    is_flag=True,
    help="Use ray or start local instance (ray init)",
)
@click.option(
    "-n",
    "--cpus",
    type=int,
    default=None,
    help="Number of CPUs to run for single-node calculations",
)
# @click.option(
#     "-l",
#     "--log-level",
#     default="info",
#     type=click.Choice(LOGGING_CHOICES, case_sensitive=False),
#     help="Logging level",
# )
@click.pass_context
def fragment(
    ctx: Context,
    project_folder: str,
    tmpdir: str,
    db_file: str,
    debug: str,
    ray: bool,
    cpus: int | None,
):
    # Configure work path
    ctx.ensure_object(dict)
    base_path = Path(project_folder) if project_folder else Path.cwd()
    # ctx.obj["log_level"] = log_level

    if ctx.invoked_subcommand not in ("init",):
        if not base_path.exists():
            raise ClickException(f"Directory '{base_path}' does not exist.")
        if not (base_path / db_file).exists():
            raise ClickException(
                f"Could not find the database named '{db_file}'. Has `fragment project init` been run?"
            )

    ctx.obj["project"] = Project(
        base_path=base_path,
        hooks={
            "calc_start": hooks.calc_start_hook,
            "calc_finish": hooks.calc_done_hook,
            "stages_add": hooks.stages_add_hook,
            "systems_add": hooks.systems_add_hook,
            "calculations_add": hooks.calculations_add,
            "calculation_status": hooks.calculation_status,
            "calculation_start_step": hooks.calculation_start_step,
            "calculation_finish_step": hooks.calculation_finish_step,
            "calculation_failed": hooks.calculation_failed,
            "wrap_driver_accessor": hooks.wrapped_driver_accessor_hook,
        },
        debug=debug,
        cpus=cpus,
        use_ray=ray, 
        tmpdir=tmpdir,
        check_migrations=ctx.invoked_subcommand != "migrate",
    )
    ctx.obj["work_path"] = base_path

    # handle the case where application is forced to fail
    if tmpdir:

        def term_handler(signum, fragme):
            print("RUNNING TERM HANDLER")
            ctx.obj["project"].__del__()

        signal.signal(signal.SIGTERM, term_handler)

    # Configure logging
    # configure_logger(level_str=log_level)

    if base_path:
        os.chdir(base_path)


@fragment.result_callback()
@click.pass_context
def fragment_cleanup(ctx, *args, **kwargs):
    # Cleanup logger
    # teardown_logger()
    if "project" in ctx.obj:
        del ctx.obj["project"]


@fragment.command(
    help="Initialize a fragment project from a strategy and a geometry file"
)
# @click.option("--migrate", is_flag=True)
# @click.option("--fake-migrations", is_flag=True)
@click.argument("strat_files", required=False, nargs=-1, type=click.Path(exists=True))
@click.pass_context
def init(ctx: click.Context, strat_files: Path):  # migrate, fake_migrations):
    project = ctx.obj["project"]
    import_strat_files(project, strat_files)


@fragment.command(help="List settings")
# @click.option("--migrate", is_flag=True)
# @click.option("--fake-migrations", is_flag=True)
@click.pass_context
def print_config(ctx: click.Context):  # migrate, fake_migrations):
    project = ctx.obj["project"]
    click.echo(summarize("CONFIGURATION", project.CONFIG.model_dump()))


@fragment.command(help="Apply Missing Migrations")
# @click.option("--migrate", is_flag=True)
# @click.option("--fake-migrations", is_flag=True)
@click.pass_context
def migrate(ctx: click.Context):  # migrate, fake_migrations):
    project: Project = ctx.obj["project"]
    _, missing = project.check_migrations()

    if not missing:
        click.echo("No missing migrations. All up to date!")
        exit()

    click.echo(
        "Migrations ensure the code and the database are in sync. "
        "Fragment will update the databse to match the current version. "
        "\n\nWARNING: Be sure to back up your fragment.bd BEFORE migrating. "
        "If the data in you database is mission critical, consider using an older version of Fragment.\n"
    )

    click.echo("These missing migrations will be applie:")
    for m, module in missing:
        click.echo(f"  {m}")

    if not click.confirm(
        "\nHave you backed up your data and do you wish to continue?"
    ):
        click.echo("Skipping migrations.")
        return
    project.run_migrations()

# from fragment.app.cli.project import project
# fragment.add_command(project)

# from fragment.app.cli.view import view
# fragment.add_command(view)

fragment.add_command(calc)
fragment.add_command(strategy)
fragment.add_command(system)


def main():
    fragment(auto_envvar_prefix="FRAGMENT")


if __name__ == "__main__":
    main()

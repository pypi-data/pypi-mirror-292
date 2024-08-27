#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from pathlib import Path

import click

from fragment.app.cli.util import import_strat_files
from fragment.project import FragmentProject as Project


@click.group(help="Project management methods")
def project():
    pass


@project.command(
    help="Initialize a fragment project from a strategy and a geometry file"
)
# @click.option("--migrate", is_flag=True)
# @click.option("--fake-migrations", is_flag=True)
@click.argument("strat_files", required=False, nargs=-1, type=click.Path(exists=True))
@click.pass_context
def init(ctx: click.Context, strat_files: Path):  # migrate, fake_migrations):
    base_path: Path = ctx.obj["work_path"]
    base_path.mkdir(exist_ok=True, parents=True)

    # This will create fragment.db
    project: Project = Project(base_path=base_path)
    import_strat_files(project, strat_files)

    # TODO: Add migration code
    # if migrate and fake_migrations:
    #     click.echo(ERROR + "Use either `--migrate` and `--fake-migrations`.")
    #     exit()

    # if migrate:
    #     click.echo("Running migrations...")
    #     project.dbm.migrate(project.basepath)
    # elif fake_migrations:
    #     click.echo("Faking migrations...")
    #     project.dbm.fake_migrations()
    # else:
    #     click.echo("Initializing Database...")
    #     try:
    #         project.init()
    #     except FileExistsError:
    #         click.echo(ERROR + "File archive already exists.")
    #     else:
    #         click.echo(INFO + "Fragment projects files were written to {work_path}")


# @project.command(help="Adds files from scratch and uploads to the file archive")
# @click.option("--remove", is_flag=True)
# @click.pass_context
# def consolodate(ctx, remove: bool = False):
#     project: Project = ctx.obj["project"]
#     if project.compressed:
#         project.consolodate_files(rm_uploads=remove)
#     else:
#         click.echo(
#             "The project is compressed. Please uncompress in order to consolodate files."
#         )
#
#    project.consolodate_files(rm_uploads=remove)


# @project.command(help="Compresses file.archive.tar into file_archive.tar.bz2")
# @click.pass_context
# def compress(ctx, remove: bool = False):
#     project: Project = ctx.obj["project"]
#     click.echo("Compressing... ", nl=False)
#     project.compress()
#     click.echo("DONE")


# @project.command(help="Uncompresses file archive from tar.bz2")
# @click.pass_context
# def uncompress(ctx, remove: bool = False):
#     project: Project = ctx.obj["project"]
#     click.echo("Uncompressing... ", nl=False)
#     project.uncompress()
#     click.echo("DONE")


# @project.command(help="Summary statistics for this project")
# @click.pass_context
# def info(ctx):
#     project: Project = ctx.obj["project"]
#     click.echo("PROJECT PATH: " + str(project.basepath))
#     click.echo(f"SYSTEMS: {project.systems_summary()}")
#     calcs = Calculation.select().count()
#     click.echo("CALCULATIONS: {}".format(calcs))
#     click.echo("JOBS:")
#     js = project.jobs_summary()
#     click.echo(f"  PENDING: {js[JobStatus.PENDING]}")
#     click.echo(f"  COMPLETED: {js[JobStatus.COMPLETED]}")
#     click.echo(f"  FAILED: {js[JobStatus.FAILED]}")
#     click.echo(f"  RUNNING: {js[JobStatus.RUNNING]}")

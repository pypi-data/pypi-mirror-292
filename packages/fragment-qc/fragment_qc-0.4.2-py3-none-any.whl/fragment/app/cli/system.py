#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import List

import click
import conformer.export as cio
from conformer.db.models import DBSystem, DBSystemLabel

from fragment.project import FragmentProject as Project


@click.group(help="Commands for handling system geometry")
def system():
    pass


@system.command(help="Read in a geometry file")
@click.option(
    "--name",
    required=True,
    prompt=True,
    help="Name slug used to uniquily identify this system",
)
@click.option("--note", required=False, prompt=True, help="A human readable comment")
@click.option(
    "-c",
    "--charges",
    required=False,
    help=(
        "List of atom charges in the file in a `id1:charge1,id2:charge2` format. "
        + "For XYZ files `id` is the 1-based index of the atom for how it appears in the file. "
        + "For PDB files `id` is the ID in the PDB file."
    ),
)
@click.argument("geometry_file", required=True, type=click.Path(exists=True))
@click.pass_context
def add(ctx, name, note, charges, geometry_file):
    project: Project = ctx.obj["project"]

    charges_dict = {}
    if charges:
        for cs in charges.split(","):
            atom, charge = cs.split(":")
            charges_dict[int(atom)] = int(charge)

    project.read_system_file(
        name, geometry_file, note=note, charges=charges, add_to_db=True
    )


@system.command(help="List systems")
@click.pass_context
def list(ctx):
    project: Project = ctx.obj["project"]

    with project:
        names = DBSystemLabel.all_system_names()
        total_systems = DBSystem.select().count()

    num_unnamed = total_systems - total_systems

    for n in names:
        click.echo(n)

    if num_unnamed:
        click.echo()
        suffex = "" if num_unnamed == 1 else "s"
        click.echo(+f"{num_unnamed} unnamed system" + suffex)


@system.command(help="Provide details on a specific system")
@click.option("--xyz", required=False, default=False, is_flag=True)
@click.option("--with-atoms", required=False, default=False, is_flag=True)
@click.option("-v", "--visualize", required=False, default=False, is_flag=True)
@click.argument("system_names", required=True, nargs=-1)
@click.pass_context
def info(ctx, system_names: List[str], xyz: bool, with_atoms: bool, visualize: bool):
    project: Project = ctx.obj["project"]

    to_query = []
    for i in system_names:
        try:
            to_query.append(int(i))
        except ValueError:
            to_query.append(i)

    systems = project.get_systems(*to_query)

    for name in to_query:
        system = systems[name]

        if xyz:
            click.echo(cio.to_xyz_str(system))
        else:
            click.echo(system.summarize(with_atoms=with_atoms))
            if visualize:
                cio.visualize(system, show_idxs=False)

    return

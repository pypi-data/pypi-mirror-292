#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import List

import click
from conformer.project import UnknowCalculationException, _pass_fn
from conformer_core.db.models import DBCalculationRecord
from conformer_core.records import RecordStatus

from fragment.project import FragmentProject as Project


@click.group(help="Calculation management")
def calc():
    pass


@calc.command(help="Lists all calculations")
@click.option(
    "--with-status",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include the status.",
)
@click.option("--with-note", is_flag=True, default=False, help="Include the note.")
@click.pass_context
def list(ctx, with_status: bool, with_note: bool):
    project: Project = ctx.obj["project"]
    with project:
        names = DBCalculationRecord.all_calculation_names()

    for name, status, note in names:
        calc = name
        if with_status:
            calc += " (" + RecordStatus(status).name + ")"
        if with_note and note:
            calc += ": " + note
        click.echo(calc)


@calc.command(help="Show calculation details")
@click.argument("calc_names", required=True, nargs=-1)
@click.pass_context
def info(ctx, calc_names: List[str]):
    project: Project = ctx.obj["project"]
    try:
        calcs = project.get_calculations(*calc_names)
    except UnknowCalculationException:
        click.echo("Unknown calculation")
        return

    for name in calc_names:
        calc = calcs[name]
        click.echo(calc.summarize())


@calc.command(help="Add new calculations")
@click.option(
    "--system", "-s", required=True, multiple=True, type=str, help="System name or ALL"
)
@click.argument("calc_steps", required=True, nargs=-1, type=str)
@click.option(
    "--name", "-n", required=False, type=str, default=None, help="Calculation note"
)
@click.option("--note", "-o", required=False, type=str, default=None, help="Note")
@click.option(
    "--run", "-r", is_flag=True, default=False, help="Run calculations after adding"
)
@click.pass_context
def add(ctx, system: List[str], calc_steps: List[str], name: str, note: str, run: bool):
    project: Project = ctx.obj["project"]
    project.add_calculations(system, calc_steps, name=name, note=note, run=run)


@calc.command(help="Run calculations")
@click.argument("calc_names", required=True, nargs=-1, type=str)
@click.option("--rerun", is_flag=True, required=False, default=False)
@click.pass_context
def run(ctx, calc_names: List[str], rerun: bool):  # TODO: Add rerun step
    project: Project = ctx.obj["project"]

    if len(calc_names) > 1 or "ALL" in calc_names:
        project.HOOKS["calculation_start_step"] = _pass_fn
        project.HOOKS["calculation_finish_step"] = _pass_fn
    try:
        project.run_calculations(*calc_names, rerun=rerun)
    except UnknowCalculationException:
        click.echo("Unknown calculation")
        return


@calc.command(help="Runs calculation and adds it in the DEBUG folder.")
@click.argument("system_names", required=True, nargs=-1, type=str)
@click.option(
    "--driver", "-s", required=True, multiple=False, type=str, help="Driver to debug"
)
@click.pass_context
def debug(ctx, system_names: List[str], driver: str):
    project: Project = ctx.obj["project"]

    systems = project.get_systems(*system_names)
    driver = project.get_stage(driver)

    dname = driver.name
    driver.provision(basepath=project.PATH / "debug" / dname)
    driver.opts.remove_files = False
    driver.configure()

    click.echo(f"DEBUGGING {dname}:")

    for system in systems.values():
        click.echo(f"  {system.name}")
        new_record = driver(system)
        print(new_record.summarize(level=2))


# @calc.command(help="Lists all calculations")
# @click.argument("name", required=True)
# @click.pass_context
# def info(ctx, name):
#     project: Project = ctx.obj["project"]
#     from fragment.calculations.models import Calculation

#     with project.dbm:
#         calc = Calculation.get(Calculation.name == name)

#         click.echo()
#         click.echo(click.style("NAME:", underline=True) + f" {calc.name}\n")
#         click.echo(click.style("NOTE:", underline=True) + f" {calc.note}\n")

#         try:
#             props = calc.properties
#         except IncompleteJobsError:
#             click.echo("    Calculation has incomplete jobs")
#             props = None

#         click.echo(click.style("LAYERS:\n", underline=True))

#         for coef, layer in zip(calc.coefs, calc.layers):
#             if coef < 0:
#                 color = "red"
#             else:
#                 color = "green"
#             coef_str = click.style(f"({coef: d}) ", fg=color)
#             click.echo(
#                 "    "
#                 + coef_str
#                 + click.style(
#                     f"{layer.view.name} ({len(layer.view.fragments)} frags)",
#                     underline=True,
#                 )
#                 + " → "
#                 + click.style(f"{layer.backend.name}", underline=True)
#                 + f": l:{layer.id}"
#             )
#             try:
#                 for k, v in layer.properties:
#                     click.echo(f"    {k:>18}: {v}")
#             except IncompleteJobsError:
#                 incomplete_jobs = layer.jobs.select(
#                     Job.status != JobStatus.COMPLETED
#                 ).count()
#                 click.echo(f"\n         INCOMPLETE JOBS: {incomplete_jobs}")
#                 continue
#             except Exception as e:
#                 click.echo(ERROR + "There was an error:")
#                 click.echo(e)
#                 exit(-2)
#             click.echo()

#         if props:
#             click.echo(click.style("PROPERTIES:\n", underline=True))

#             if props:
#                 for k, v in props:
#                     click.echo(f"    {k:>18}: {v}")

#             click.echo()


# @calc.command(help="Run all jobs in calculation")
# @click.option("-r", "--rerun-failed", is_flag=True, help="Run Failed Jobs")
# @click.option("-v", "--verbose", is_flag=True, help="Print out verbose errors")
# @click.argument("calcs", required=True, nargs=-1, type=str)
# @click.pass_context
# def run(ctx, rerun_failed, verbose, calcs: List[str]):
#     project: Project = ctx.obj["project"]
#     with project.dbm:
#         worker = Worker(cores=ctx.obj["cores"])
#         worker.save()

#     if "ALL" in calcs:
#         calcs = ["ALL"]

#     # TODO: Allow batching
#     for calc_name in calcs:
#         with project.dbm:
#             try:
#                 if calc_name.lower().startswith("j:"):
#                     # We are running a single job
#                     job_id = int(calc_name.split(":")[1])
#                     query = Job.select().where(Job.id == job_id)
#                 elif calc_name.lower().startswith("l:"):
#                     layer_id = int(calc_name[2:])
#                     query = Layer.get(layer_id).jobs
#                 elif calc_name == "ALL":
#                     query = Job.select()
#                 else:
#                     query = Calculation.get(name=calc_name).jobs
#             except Exception as e:
#                 # raise e
#                 click.echo(WARNING + f"Unknown calculation '{calc_name}'. Skipping")
#                 continue

#             click.echo(INFO + f"Running {calc_name}🏃", nl=False)

#             backend: QMBackend = None
#             with project.open_archive("a") as arch:
#                 for job in Job.exclude_complete(query, rerun_failed).iterator():
#                     job: Job
#                     if backend is None or backend.conf_id != job.backend__id:
#                         backend = job.backend

#                     res: Result = project.run_job(
#                         job, worker=worker, backend=backend, archive=arch, rerun=True
#                     )
#                     project.dbm.context_db.commit()
#                     if res.status != JobStatus.COMPLETED:
#                         error_str = f"E(j:{job.id})"
#                         click.echo(click.style(error_str, fg="red"), nl=False)
#                     else:
#                         click.echo(".", nl=False)
#             click.echo()

#         click.echo()
#         with project.dbm:
#             worker: Worker = Worker.get(worker.id)  # The project will
#             # update without refreshing
#         click.echo(INFO + f"{worker.jobs_handled} jobs ran")
#         if worker.jobs_succeeded:
#             click.echo(SUCCESS + f"{worker.jobs_succeeded} jobs succeeded 🥳")
#         if worker.jobs_failed:
#             click.echo(ERROR + f"{worker.jobs_failed} jobs have failed 🤬")


# def value_or_NA(V: Any):
#     if V is None:
#         return V
#     return V.value


# @calc.command(help="Re-extracts properties for all completed")
# @click.option("--all", is_flag=True, help="Extract properties from all completed jobs")
# @click.pass_context
# def collect_properties(ctx, all):
#     click.echo(INFO + "Updating properties will overwrite any previouse values")
#     con: str = click.prompt("Would you like to continue? [y/n]")

#     if not con.lower().startswith("y"):
#         return

#     project: Project = ctx.obj["project"]
#     fs_handler = ctx.obj["fs_handler"]
#     worker = Worker()
#     worker.configure(fs_handler)
#     from fragment.calculations.models import Job, JobStatus

#     with project.dbm:
#         jobs_query: Iterable[Job] = Job.select().where(
#             Job.status == JobStatus.COMPLETED
#         )
#         if not all:
#             jobs_query: Iterable[Job] = jobs_query.where(Job.properties == {})
#             click.echo(INFO + "Updating blank properties...")
#         else:
#             click.echo(INFO + "Updating all properties could take long time...")

#         for job in jobs_query:
#             job.update_properties_from_workdir(
#                 worker.job_filename_stub(job), worker.job_abs_workdir(job)
#             )
#             job.save()


# @calc.command(help="Outputs a CSV summary of all completed calculations")
# @click.argument("output_file")
# def summary(output_file):
#     import csv

#     from fragment.calculations.models import Calculation, Job, Layer

#     # TODO: Add hybrid property for completed
#     rows: List[PropertySet] = []
#     for calc in Calculation.select():
#         try:
#             rows.append(
#                 (
#                     calc.name,
#                     calc.get_properties(),
#                 )
#             )
#         except IncompleteJobsError:
#             pass
#     keys = set()
#     for _, prop in rows:
#         for k in prop.properties.keys():
#             keys.add(k)

#     # Print the header
#     with open(output_file, "w") as f:
#         writer = csv.writer(f)
#         writer.writerow(["calc_name"] + [k for k in keys])
#         for name, params in rows:
#             writer.writerow(
#                 [name] + [value_or_NA(params.properties.get(k, None)) for k in keys]
#             )

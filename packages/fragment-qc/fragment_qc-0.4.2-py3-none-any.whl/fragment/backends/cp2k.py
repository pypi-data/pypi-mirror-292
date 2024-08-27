#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import subprocess
import time
from datetime import datetime
from os import environ

from fragment.backends.abstract import QMShellCommand
from fragment.backends.common import RunContext
from fragment.properties.extraction import calc_property

ZERO = 1e-9


class CP2KBackend(QMShellCommand):
    DEFAULT_TEMPLATE_PARAMS = {
        "template": """\
        {n_atoms}
        {name}: n_atoms={n_atoms};
        {geometry}
        """,
        "atom": "{symbol}    {x} {y} {z}",
    }
    FILE_MANIFEST = {
        "input": ".inp",
        "geometry": ".xyz",
        "potential": ".pot",
        "output": ".out",
        "log": ".log",
    }
    EXTRACTABLE_FILES = ("output",)
    # CP2K tends to have multiple names for the exec. so we will configure this at runtime
    RUN_CMD = environ.get("CP2K_EXEC", "cp2k")

    def __init__(
        self, *args, input_template=None, potential_file=None, **kwargs
    ) -> None:
        self.input_template = input_template
        self.potential_file = potential_file
        super().__init__(
            *args,
            input_template=input_template,
            potential_file=potential_file,
            **kwargs
        )

    def setup_calc(self, ctx: RunContext):
        super().setup_calc(ctx)

        # Get the run command
        ctx.scratch["run_cmd"], ctx.scratch["run_args"] = self.get_run_cmd(ctx)

        environ["OMP_NUM_THREADS"] = str(ctx.cores)

        # TODO: Make this more customizable
        # Write the input file
        # Fails if there isn't this file so make a dummy
        with ctx.files["potential"].open("w") as f:
            if self.potential_file:
                f.write(self.potential_file)

        with ctx.files["geometry"].open("w") as f:
            f.write(
                self.template.system_to_string(
                    ctx.system,
                    num_atoms=len(ctx.system.atoms),
                    name=ctx.name,
                    time=datetime.now().isoformat(),
                    system_id=ctx.system.id,
                    backend=self.name,
                    cores=ctx.cores,
                )
            )

        with ctx.files["input"].open("w") as f:
            f.write(
                self.input_template.format(
                    name=ctx.name,
                    charge=ctx.system.charge,
                    multiplicity=ctx.system.multiplicity,
                    num_atoms=len(ctx.system.atoms),
                    potential_file=ctx.files["potential"].absolute(),
                    geometry_file=ctx.files["geometry"].absolute(),
                )
            )

    @classmethod
    def is_available(cls):
        try:
            return (
                subprocess.run(
                    cls.RUN_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                ).returncode
                == 0
            )
        except FileNotFoundError:
            return False

    def get_run_cmd(self, ctx: RunContext) -> None:
        # This may not work for non-MPI versin of CP2K.
        cmd = environ.get("CP2K_EXE", self.RUN_CMD)

        # We will only allow single-node mode for simplicity
        # OMP_NUM_THREADS should be set by this point
        return cmd, [
            "-i",
            ctx.files["input"],
            "-o",
            ctx.files["output"],
        ]

    def run_calc(self, ctx: RunContext):
        cpu0 = time.process_time()
        ret = super().run_calc(ctx)
        ctx.scratch["cpu_time"] = time.process_time() - cpu0
        return ret

    @calc_property(source="context")
    def prop_cpu_time(self, ctx: RunContext):
        """This is the single node time."""
        return ctx.scratch.get("cpu_time", None)

    @calc_property(
        source="re_file",
        take_last=True,
        patterns=[r"Total energy: +([\d\-\.]+)"],
    )
    def prop_total_scf_energy(self, ctx: RunContext, m, _):
        return float(m[1])

    @calc_property(
        source="re_file",
        patterns=[
            r"ENERGY\| Total FORCE_EVAL \( QS \) energy \[a\.u\.\]: +([\d\-\.]+)"
        ],
    )
    def prop_total_energy(self, ctx: RunContext, m, _):
        return float(m[1])

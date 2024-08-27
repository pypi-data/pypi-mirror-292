#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from fragment.backends.common import RunContext
from fragment.backends.cp2k import CP2KBackend
from fragment.backends.util import get_backend
from fragment.calculations.models import JobStatus
from fragment.systems.models import Atom
from tests._util import DBTestCase, make_system
from tests.backends.util import H2_job

INPUT_TEMPLATE = """\
&GLOBAL
  PROJECT {name}
  PRINT_LEVEL LOW
  RUN_TYPE ENERGY
&END GLOBAL

&FORCE_EVAL
  METHOD QS
  &DFT
    CHARGE {charge}
    BASIS_SET_FILE_NAME BASIS_MOLOPT
    POTENTIAL_FILE_NAME {potential_file}
    &MGRID
        COMMENSURATE 
        CUTOFF 400
        NGRIDS 5
    &END MGRID
    &QS
      EPS_DEFAULT 1.0E-14
      EXTRAPOLATION ASPC
      EXTRAPOLATION_ORDER 3
    &END QS
    &SCF
      SCF_GUESS ATOMIC
      MAX_SCF 30
      EPS_SCF 1.0E-6
      &OT
        MINIMIZER DIIS
        PRECONDITIONER FULL_ALL
      &END OT
      &OUTER_SCF
          MAX_SCF 10
          EPS_SCF 1.0E-6
      &END OUTER_SCF
    &END SCF
    &XC
      &XC_FUNCTIONAL
        &PBE
          PARAMETRIZATION REVPBE
        &END PBE
      &END XC_FUNCTIONAL
      &vdW_POTENTIAL
        DISPERSION_FUNCTIONAL PAIR_POTENTIAL
        &PAIR_POTENTIAL
          TYPE DFTD3
          PARAMETER_FILE_NAME dftd3.dat
          REFERENCE_FUNCTIONAL revPBE
        &END
      &END vdW_POTENTIAL
    &END XC
    &POISSON
      POISSON_SOLVER WAVELET
      PERIODIC NONE
    &END POISSON
  &END DFT
  
  &SUBSYS
    &CELL
      ABC 5 5 5
      PERIODIC NONE
    &END CELL
    &TOPOLOGY
      COORD_FILE_NAME {geometry_file}
      COORD_FILE_FORMAT XYZ
      &CENTER_COORDINATES 
      &END CENTER_COORDINATES 
    &END TOPOLOGY
    &KIND O
      BASIS_SET DZVP-MOLOPT-GTH-q6
      POTENTIAL GTH-revPBE-q6
    &END KIND
    &KIND H
      BASIS_SET DZVP-MOLOPT-GTH-q1
      POTENTIAL GTH-revPBE-q1
    &END KIND
  &END SUBSYS

  &PRINT
    &FORCES
      &EACH
        MD 1
      &END EACH
      FILENAME =init_forces.out
    &END FORCES
  &END PRINT
&END FORCE_EVAL

&MOTION
  &MD
    ENSEMBLE NVT
    STEPS 4800
    TIMESTEP 0.5
    TEMPERATURE 298.15
    &THERMOSTAT
       TYPE NOSE
    &END THERMOSTAT
  &END MD
  &PRINT
    &TRAJECTORY                                 ! Controls the output of the trajectory
      FORMAT XYZ                                ! Format of the output trajectory is DCD
      &EACH
        MD 1
      &END EACH
    &END TRAJECTORY
    &RESTART                                    ! This section controls the printing of restart files
      &EACH
        MD 1
      &END EACH
    &END RESTART
  &END PRINT
&END MOTION
&END
"""

POTENTIAL_FILE = """\
#
H GTH-revPBE-q1
	1	0	0	0
	0.20016995890943	2	-4.17620500156816	0.72331890028322
	0
#
N GTH-revPBE-q5
	2	3	0	0
	0.28170297703800	2 -12.44749931239895	1.88552287889776
	1
	0.25546700814149	1	13.57047242882571
#
C GTH-revPBE-q4
	2	2	0	0
	0.33844318955221	2	-8.72754824830209	1.34292529706254
	1
	0.30251428183120	1	9.61143874244521
#
O GTH-revPBE-q6
	2	4	0	0
	0.23926594896015	2 -16.93098298728737	2.52854372456023
	1
	0.22052348957419	1	18.42348732424916
#
K GTH-revPBE-q9
	3	6	0	0
	0.39250464514581	2	-3.36355185931784	-1.05652974706380
	2
	0.30531773770277	2	17.85062322518532	-5.62264869939036
	7.26130826238767
	0.31656802191361	2	7.33378021694260	-2.46094504966893
	2.91120443661679
#
Al GTH-revPBE-q3
	2	1	0	0
	0.43522493716126	2	-8.27253615740789	0.12340152465836
	2
	0.48743074481381	2	6.92421170398871	-1.88883583255700
	2.44150480767714
	0.56259598095577	1	1.86709197536867
#
Si GTH-revPBE-q4
	2	2	0	0
	0.43224079969648	1	-6.26928834981876
	2
	0.43563382750146	2	8.90861648065539	-2.70627081846166
	3.50378060414596
	0.49794218773404	1	2.43127674242674
#
Cl GTH-revPBE-q7
	2	5	0	0
	0.412034522378	2	-6.387383124731	-0.009021846686
	2
	0.339499063755	2	15.221166054129	-4.941683697911
	6.377370338332
	0.378779796494	1	4.341201779417
#
Zn GTH-revPBE-q12
	2	0	10	0
	0.51000000228344	0
	3
	0.40031643972938	3	11.53004133325909	-8.79189815087765	3.14508644050535
	16.46577517823516	-8.12057826991473
	6.44550918109619
	0.54318233049508	2	2.59719511863852	-0.59426275777150
	0.70314116434215
	0.25095883990735	1 -14.46695794737136
#
Zn GTH-revPBE-q20
	4	6	10	0
	0.34729494527940	2	0.55188457612508	1.24394371538092
	3
	0.24394891392819	2	-1.34762692127901	12.79313122006917
	-16.51586127796785
	0.23975357983051	2	-9.72145778524195	8.07114354774031
	-9.54990573621412
	0.20855197150871	1 -14.19380886456333
#
Li GTH-revPBE-q3
	3	0	0	0
	0.40000000000000	4 -14.08115455000000	9.62621962000000	-1.78361605000000	0.08515207000000
	0
#
I GTH-revPBE-q7
	2	5	0	0
	0.56097542412968	1	8.30696737704382
	3
	0.53192813005532	3	2.30814580951754	1.00390933198339	-0.95915606171248
	-2.85610798585839	2.47653030126803
	-1.96568497424122
	0.58918243972806	2	0.90648219018486	0.42507060006662
	-0.50295032038699
	0.74085157566198	1	0.47919458163563
#
Be GTH-revPBE-q4
	4	0	0	0
	0.32499880271667	4 -24.07750832805718	17.29795124769334	-3.34457120268635	0.16592706571054
	0
#
Ca GTH-revPBE-q10
	4	6	0	0
	0.37678047893891	2	-4.18920270368861	-1.58269419211563
	3
	0.28959658426544	2	20.60271759134962	-7.12978577970040
	9.20451388087920
	0.32798190506635	2	5.80560515445721	-0.42875335998725
	0.50730783345657
	0.66395554334508	1	0.05806812816398
#
Mg GTH-revPBE-q10
	4	6	0	0
	0.19368897937368	2 -20.57355447707430	3.03432071800105
	2
	0.14135522938540	1	41.04812203589492
	0.10309633839049	1	-9.99181442015447
#
F GTH-revPBE-q7
	2	5	0	0
	0.21567445455070	2 -21.48683351622989	3.21178110848798
	1
	0.19458888073306	1	23.75455185056465
#
Pb GTH-revPBE-q4
	2	2	0	0
	0.62653984021894	1	4.80942462908873
	3
	0.62239090790603	3	0.91062966105019	2.08114783414933	-1.43125709514796
	-5.01469015497042	3.69548993848729
	-2.93320024763669
	0.82127204767750	2	0.15775036263689	0.47889785159446
	-0.56326396709903
	1.02293599354606	1	0.35389806040014
#
Pb GTH-revPBE-q14
	2	2	10	0
	0.52999999956377	1	12.57214280289374
	3
	0.49588591819966	2	8.41124414880275	-3.44005610001354
	4.48109332262415
	0.56934785269083	2	4.92900648134337	-2.89639919972065
	3.42706575600028
	0.40422412959527	2	-6.81491261568961	1.83782672991795
	-2.08389963461851
#
Na GTH-revPBE-q9
	3	6	0	0
	0.273005790125	2	0.338497427794	-0.626328732556
	2
	0.125922383347	1	34.093580226825
	0.147350171683	1 -14.234385268353
"""


class CP2KTestCases(DBTestCase):
    def setUp(self) -> None:
        self.backend: CP2KBackend = get_backend("CP2K")("cp2k", "")
        self.sys = make_system(atoms=2)

    def test_atom(self):
        atom = Atom.get(1)
        self.assertEqual(
            self.backend.template.atom_to_string(atom),
            "H    0.0 0.0 0.0",
        )

    @unittest.skip("Not implemented yet")
    def test_ghost_atom(self):
        """CP2K Use a custom kinds command which isn't yet implemented"""
        ...

    def test_template(self):
        out_templ = self.backend.template.system_to_string(self.sys, name="fragment_1")
        self.assertEqual(
            out_templ,
            dedent(
                """\
            2
            fragment_1: n_atoms=2;
            H    0.0 0.0 0.0
            H    1.0 1.0 1.0
            """
            ),
        )

    def test_properties(self):
        props = self.backend.get_properties(
            RunContext(1, "name", self.sys),
            [
                StringIO(
                    dedent(
                        """\
                Total energy:                                              -300.78929943899482

                Electronic density on regular grids:       -159.9999999893        0.0000000107
                Core density on regular grids:              160.0000000000       -0.0000000000
                Total charge density on r-space grids:        0.0000000107
                Total charge density g-space grids:           0.0000000107

                Overlap energy of the core charge distribution:               0.00000088824974
                Self energy of the core charge distribution:               -905.25177057963435
                Core Hamiltonian energy:                                    262.27942861330308
                Hartree energy:                                             384.04309225768105
                Exchange-correlation energy:                                -85.78730192468535
                Dispersion energy:                                           -0.07274869390892

                Total energy:                                              -344.78929943899482

                outer SCF iter =    2 RMS gradient =   0.45E-06 energy =       -344.7892994390
                outer SCF loop converged in   2 iterations or   26 steps


                ENERGY| Total FORCE_EVAL ( QS ) energy [a.u.]:             -344.789299439551201
            """
                    )
                )
            ],
        )
        self.assertDictEqual(
            props.to_dict(),
            {
                "total_scf_energy": -344.7892994389948,
                "total_energy": -344.7892994395512,
            },
        )

    @unittest.skipIf(not CP2KBackend.is_available(), "Could not find cp2k exe")
    def test_exec(self):
        backend: CP2KBackend = get_backend("CP2K")(
            "cp2k", "", input_template=INPUT_TEMPLATE, potential_file=POTENTIAL_FILE
        )
        backend.save_config()
        job = H2_job(backend)

        with TemporaryDirectory() as dir:
            res = backend.run(
                job.id, "test_job", job.modded_system, 1, workpath=Path(dir)
            )

        # Now checkout how our job went :)
        self.assertEqual(res.status, JobStatus.COMPLETED)
        self.assertAlmostEqual(res.properties["total_energy"], -1.16302222, 5)
        self.assertAlmostEqual(res.properties["total_scf_energy"], -1.16302222, 5)

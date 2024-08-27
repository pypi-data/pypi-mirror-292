#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from enum import Enum
from typing import Dict, List, Optional, Union

import pydantic
from typing_extensions import Literal

from .common import FragmentBaseModel, NamedAndNotedModel

# ===========================================================================
#                            MODS
# ===========================================================================


class ModModel(NamedAndNotedModel):
    mod_name: str


class RCapsModel(ModModel):
    mod_name: Literal["rcaps", "RCaps"]
    tolerance: Optional[float]
    cutoff: Optional[float]
    k: Optional[int]
    ignore_charged: Optional[bool]


class DistanceModModel(ModModel):
    mod_name: Literal["distance", "Distance"]
    method: Optional[Literal["com", "COM", "closest", "Closest"]]
    min_distance: Optional[Union[float, Dict[int, float]]]
    max_distance: Optional[Union[float, Dict[int, float]]]
    distance: Optional[Union[float, Dict[int, float]]]  # Depricated


class xTBEnergyModModel(ModModel):
    mod_name: Literal["xtbenergy", "xTBEnergy", "XTBEnergy"]
    backend: str
    thresholds: Dict[int, float]


class xTBChildrenEnergyModModel(ModModel):
    mod_name: Literal["xtchildrenbenergy", "xTBChildrenEnergy", "XTBChildrenEnergy"]
    backend: str
    thresholds: Dict[int, float]


class xTBChildrenEnergyProductModModel(ModModel):
    mod_name: Literal[
        "xtchildrenbenergyproduct",
        "xTBChildrenEnergyProduct",
        "XTBChildrenEnergyProduct",
    ]
    backend: str
    thresholds: Dict[int, float]


class EnergyNodeTrimmingModModel(ModModel):
    mod_name: Literal["energy_trimming", "EnergyTrimming"]
    backend: str
    thresholds: Dict[int, float]


class UseSupersystemBasisModModel(ModModel):
    mod_name: Literal[
        "UseSupersystemBasis", "usesupersystembasis", "use_supersystem_basis"
    ]


class ClutserBasisModModel(ModModel):
    mod_name: Literal["ClusterBasis", "cluster_basis", "clusterbasis"]


class UseCloudBasisModModel(ModModel):
    mod_name: Literal["UseCloudBasis", "usecloudbasis", "use_cloud_basis"]
    cutoff: Optional[float]


class MICFilterModel(ModModel):
    mod_name: Literal["MICFilter", "micfilter"]
    a: float
    b: float
    c: float


class MICWrapSystem(ModModel):
    mod_name: Literal["MICWrapSystem", "micwrapsystem"]
    a: float
    b: float
    c: float


ModTypes = Union[
    RCapsModel,
    DistanceModModel,
    xTBEnergyModModel,
    xTBChildrenEnergyModModel,
    xTBChildrenEnergyProductModModel,
    ClutserBasisModModel,
    UseSupersystemBasisModModel,
    UseCloudBasisModModel,
    MICFilterModel,
    MICWrapSystem,
]
# ===========================================================================
#                            SUPERSYSTEM
# ===========================================================================


class SubsystemModel(NamedAndNotedModel):
    include: Optional[str]
    exclude: Optional[str]


class SupersystemModel(NamedAndNotedModel):
    source: pydantic.FilePath
    charges: Optional[Dict[int, int]]
    subsystems: Optional[List[SubsystemModel]]


# ===========================================================================
#                            BACKENDS
# ===========================================================================


class BackendModel(NamedAndNotedModel):
    program: str
    template: Optional[str]


class BackendQChem(BackendModel):
    program: Literal["qchem", "QChem"]


class BackendCP2k(BackendModel):
    program: Literal["CP2K", "cp2k"]
    input_template: str
    potential_file: Optional[str]


class BackendXYZ(BackendModel):
    program: Literal["xyz", "XYZ"]


class BackendORCA(BackendModel):
    program: Literal["orca", "ORCA"]


class BackendNWChem(BackendModel):
    program: Literal["nwchem", "NWCHEM", "NWChem"]


class BackendXTB(BackendModel):
    program: Literal["xTB", "xtb", "XTB"]
    memory: Optional[float]


class XTBMethods(Enum):
    GFN2 = "gfn2"
    GFN1 = "gfn1"
    GFN0 = "gfn0"
    IPEA = "ipea"
    GFNFF = "gfnff"


class BackendLibXTB(BackendModel):
    program: Literal["libxtb", "LibXTB", "LibxTB"]
    method: Optional[str]
    accuracy: Optional[float]


class PySCF_Procedure(FragmentBaseModel):
    method: str
    basis: str
    conv_tol: float = 1e-9
    direct_scf_tol: float = 1e-14
    driver: Optional[str]
    use_newton: bool = False


class PySCF_HF(PySCF_Procedure):
    method: Literal["hf", "HF"]


class PySCF_KS(PySCF_Procedure):
    method: Literal["ks", "KS", "dft", "DFT"]
    xc: str


class PySCF_MP2(PySCF_HF):
    method: Literal["mp2", "MP2"]
    mp2_driver: Optional[str]


class PySCF_DFMP2(PySCF_MP2):
    method: Literal["dfmp2", "DFMP2", "rimp2", "RIMP2"]
    auxbasis: Optional[str]


class PySCF_CCSD(PySCF_HF):
    method: Literal["ccsd", "CCSD"]


class PySCF_CCSD_T(PySCF_CCSD):
    method: Literal["ccsd(t)", "CCSD(T)", "ccsd_t", "CCSD_T"]


PYSCF_PROC_LIST = Union[
    PySCF_HF, PySCF_KS, PySCF_MP2, PySCF_DFMP2, PySCF_CCSD, PySCF_CCSD_T
]


class BackendPySCF(BackendModel):
    program: Literal["pyscf", "PySCF", "PYSCF"]
    procedure: PYSCF_PROC_LIST


class BackendMOPAC(BackendModel):
    program: Literal["MOPAC", "mopac", "MOPAC2016"]


BackendTypes = Union[
    BackendQChem,
    BackendCP2k,
    BackendXYZ,
    BackendORCA,
    BackendXTB,
    BackendLibXTB,
    BackendMOPAC,
    BackendPySCF,
]
# ===========================================================================
#                            FRAGMENTERS
# ===========================================================================


class FragmenterBase(NamedAndNotedModel):
    fragmenter: str
    mods: Optional[List[str]]
    combinator: Optional[Literal["bottom_up", "top_down", "mbe"]]
    bu_missing: Optional[int] = 0


class FragmenterPDB(FragmenterBase):
    fragmenter: Literal["PDB", "pdb"]


class FragmenterWater(FragmenterBase):
    fragmenter: Literal["water", "Water"]


class FragmenterSupersystem(FragmenterBase):
    fragmenter: Literal["Supersystem", "supersystem"]


class FragmenterRaw(FragmenterBase):
    fragmenter: Literal["Raw", "raw"]


class FragmenterCompound(FragmenterBase):
    fragmenter: Literal["Compound", "compound"]
    fragments: Dict[str, str]
    default: Optional[str]


class FragmenterMBCP(FragmenterBase):
    fragmenter: Literal["mbcp", "MBCP"]


class FragmenterBSSEBalanced(FragmenterBase):
    fragmenter: Literal["BSSEBalanced", "bssebalanced"]


FragmenterTypes = Union[
    FragmenterPDB,
    FragmenterRaw,
    FragmenterCompound,
    FragmenterWater,
    FragmenterSupersystem,
    FragmenterMBCP,
    FragmenterBSSEBalanced,
]
# ===========================================================================
#                            VIEW
# ===========================================================================


class PartialViewModel(FragmentBaseModel):
    order: int
    fragmenter: str  # Convert to Abstract Fragmenter


class ViewModel(PartialViewModel):
    system: str  # Convert to System


# ===========================================================================
#                            LAYER
# ===========================================================================


class LayerModel(FragmentBaseModel):
    backend: str  # Convert to
    view: PartialViewModel  # Convert to proper view
    mods: Optional[List[str]]


# ===========================================================================
#                            CALCULATION
# ===========================================================================


class CalculationModel(NamedAndNotedModel):
    system: Union[
        Literal["ALL"],  # Run the calculation on all supersystems
        List[str],  # Run the calculation all the listed system
        str,  # Run the calculation on a single system
    ]
    layers: List[LayerModel]


# ===========================================================================
#                            THE STRATEGY FILE
# ===========================================================================


class Strategy(FragmentBaseModel):
    mods: Optional[List[ModTypes]]
    systems: Optional[List[SupersystemModel]]
    backends: Optional[List[BackendTypes]]
    fragmenters: Optional[List[FragmenterTypes]]
    calculations: Optional[List[CalculationModel]]

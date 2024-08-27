#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import Any, Dict, List, Optional, Tuple

import pydantic

from fragment.systems.common import AtomType

from .common import FragmentBaseModel


class Atom(FragmentBaseModel):
    id: Optional[int]  # Database ID
    t: str
    r: List[float]
    charge: int
    type: AtomType
    meta: Optional[Dict[str, Any]]

    @pydantic.validator("r", pre=True)
    def np_to_list(cls, r):
        return list(r)


class System(FragmentBaseModel):
    id: Optional[int]
    key: Optional[Tuple[int, ...]]
    atoms: List[Atom]

    @pydantic.validator("atoms", pre=True)
    def manager_to_list(cls, atoms):
        return list(atoms)  # Collect the atom manager


class ConfigModel(FragmentBaseModel):
    id: int
    name: str
    config_type: str  # This should change in a future DB migration
    config_class: str  # Resolved to class by Savable Config
    args: List[Any]
    kwargs: Dict[Any, Any]  # Let's hope they are all JSON serializable


# TODO: Add view models for recreating graphs

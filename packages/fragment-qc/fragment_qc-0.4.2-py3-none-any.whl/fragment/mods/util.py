#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from fragment.mods.abstract import ModBaseClass
from fragment.registry import REGISTRY


def get_mod(mod_name: str) -> ModBaseClass:
    return REGISTRY.get_from_namespace("mod", mod_name.lower())


class UnknownMod(Exception):
    pass

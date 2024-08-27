#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import enum


class AtomType(enum.IntEnum):
    # Physical atom types
    PHYSICAL = 0  # Actual atom
    PROXY = 1  # Represents another atom (e.g. a cap)
    GHOST = 2  # Only include basis functions

    POINT_CHARGE = 3
    DUMMY = 4  # A null atom


class RelationType(enum.IntEnum):
    SUPERSYSTEM = 0
    PARENT_CHILD = 1
    DEPENDS_ON = 2  # Calculations that must happen first


class ViewType(enum.IntEnum):
    PRIMARY = 0
    AUXILIARY = 1
    PRIMATIVE = 2

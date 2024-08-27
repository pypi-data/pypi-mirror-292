#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import Any

from fragment.core.quickPIE import quickNodeList, quickNodeSet


def QNList(*kl: Any) -> quickNodeList:
    return [frozenset(i) for i in kl]


def QNSet(*ks: Any) -> quickNodeSet:
    return {frozenset(i) for i in ks}


def QNSet_ints(*ks: Any) -> quickNodeSet:
    return {frozenset({i}) for i in ks}

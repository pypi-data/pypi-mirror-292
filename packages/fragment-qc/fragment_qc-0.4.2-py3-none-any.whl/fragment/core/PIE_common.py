#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#

# CONSTANTS
from typing import Iterable, Iterator, List, Set, Tuple

ROOT = frozenset()


# TYPING
Key = Tuple[int, ...]
NodeData = Set[int]
KeySet = Set[Key]
NDList = List[NodeData]


# FUNCTIONS
def mk_key(data: Iterable[int]) -> frozenset:
    return frozenset(data)


def key_to_data(k: Key) -> NodeData:
    return set(k)


def merge_data(*nd: NodeData) -> NodeData:
    return set.union(*nd)


def merge_keys(*keys: Key) -> Key:
    return mk_key(merge_data(*NDs_from_KeySet(keys)))


def NDs_from_KeySet(ks: KeySet) -> Iterator[NodeData]:
    return [set(k) for k in ks]


def Keys_from_NDList(ndl: NDList) -> Iterator[Key]:
    return {mk_key(nd) for nd in ndl}


def get_order(data: NodeData, parents: NDList) -> int:
    return sum((1 for p in parents if p.issubset(data)))

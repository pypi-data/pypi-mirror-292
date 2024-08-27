#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pydantic

from fragment.calculations.common import JobStatus
from fragment.properties.core import PropertySet

from .common import FragmentBaseModel
from .db import System


class PartialRunContext(FragmentBaseModel):
    id: int
    name: str
    workpath: Path
    system: System
    backend_id: int  # This is not in the fragment-level version
    # Will need to be fleshed out by worker


class Result(FragmentBaseModel):
    id: int
    name: str
    status: JobStatus
    start_time: datetime
    end_time: datetime
    properties: Dict[Any, Any]

    # Expected to be paired with a UploadFile with the supporting files
    @pydantic.validator("properties", pre=True)
    def PropertySet_to_Dict(cls, v):
        if isinstance(v, PropertySet):
            return v.to_dict()
        return v


class Batch(FragmentBaseModel):
    jobs: List[PartialRunContext]


class BatchResult(FragmentBaseModel):
    start_time: datetime
    end_time: datetime
    results: List[Result]

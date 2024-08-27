#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import pydantic


class FragmentBaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True


class NamedAndNotedModel(FragmentBaseModel):
    name: str
    note: str

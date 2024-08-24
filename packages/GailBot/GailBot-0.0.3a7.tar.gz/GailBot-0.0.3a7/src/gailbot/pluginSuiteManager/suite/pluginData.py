# -*- coding: utf-8 -*-
# @Author: Vivian Li
# @Date:   2024-01-29 13:26:17
# @Last Modified by:   Vivian Li
# @Last Modified time: 2024-04-10 22:00:14
# @Description: Define the schema for data related to a single plugin suite
from typing import List, Optional
from pydantic import BaseModel


class MetaData(BaseModel):
    Version: str
    Author: str
    Email: str
    BucketName: Optional[str] = ""
    ObjectName: Optional[str] = ""
    ObjectUrl: Optional[str] = ""


class PluginDict(BaseModel):
    """dictionary type for individual plugin"""

    plugin_name: str
    dependencies: List[str]
    rel_path: str
    hidden: bool


class ConfModel(BaseModel):
    """dictionary type for plugin suite configuration dictionary"""

    metadata: MetaData
    suite_name: str
    plugins: List[PluginDict]

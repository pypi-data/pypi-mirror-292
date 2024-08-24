"""
Pydantic schemas for Protium
"""

from typing import Annotated, Any, Dict, List

from pydantic import BaseModel, Field, constr


class BaseNodeDataModel(BaseModel):
    """Base data model for node data"""

    # node 使用的模版 name，必填
    template: Annotated[str, constr(min_length=1)] = Field(..., title="Template name used by the node")
    # 使用的模版版本，不填写则默认最新版本
    version: str | None = Field(None, title="Template version used by the node")
    # body source 的参数，键为 body key，值为 body.source
    params: Dict[str, Any] | None = Field(default_factory=dict, title="Parameters for body source")
    # target handles 的连接来源，键为 handle key，值为 node key 的列表
    handles: Dict[str, List[str]] | None = Field(default_factory=dict, title="Handles connection source")


class BaseWorkflowDataModel(BaseModel):
    """Base data model for workflow data"""

    # name, optional
    name: str | None = Field("untitled", title="Name of the workflow")
    # description, optional
    description: str | None = Field("", title="Description of the workflow")
    # nodes, required
    nodes: Dict[str, BaseNodeDataModel] = Field(..., title="Nodes in the workflow")

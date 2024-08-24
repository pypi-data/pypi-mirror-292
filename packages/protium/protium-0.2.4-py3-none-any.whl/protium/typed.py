from typing import Any, List, Required, TypedDict


class BaseNodeDataProps(TypedDict, total=False):
    # node 使用的模版 name，必填
    template: Required[str]
    # 使用的模版版本，不填写则默认最新版本
    version: str
    # body source 的参数，键为 body key，值为 body.source
    params: dict[str, Any]

    # target handles 的连接来源，键为 handle key，值为 node key 的列表
    handles: dict[str, List[str]]


class BaseWorkflowDataProps(TypedDict, total=False):
    # name, optional, default: untitled
    name: str
    # description, optional
    description: str
    nodes: dict[str, BaseNodeDataProps]


class WorkflowApiResProps(TypedDict, total=False):
    uuid: str
    creator: str
    url: str
    name: str
    description: str
    created_at: str
    updated_at: str
    public: bool
    status: str

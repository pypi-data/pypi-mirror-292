from datetime import datetime
from typing import List, Union

from pydantic.main import BaseModel
from spaceone.core import utils

__all__ = [
    "WorkspaceGroupResponse",
    "WorkspaceGroupsResponse",
    "WorkspaceGroupUserSummaryResponse",
    "WorkspaceGroupUsersSummaryResponse",
]

from spaceone.identity.model.workspace_group.request import State


class WorkspaceGroupResponse(BaseModel):
    workspace_group_id: Union[str, None] = None
    name: Union[str, None] = None
    workspaces: Union[list, None] = None
    users: Union[list, None] = None
    tags: Union[dict, None] = None
    created_by: Union[str, None] = None
    updated_by: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class WorkspaceGroupsResponse(BaseModel):
    results: List[WorkspaceGroupResponse]
    total_count: int


class WorkspaceGroupUserSummaryResponse(BaseModel):
    user_id: str
    name: str
    state: State


class WorkspaceGroupUsersSummaryResponse(BaseModel):
    results: List[WorkspaceGroupUserSummaryResponse]
    total_count: int

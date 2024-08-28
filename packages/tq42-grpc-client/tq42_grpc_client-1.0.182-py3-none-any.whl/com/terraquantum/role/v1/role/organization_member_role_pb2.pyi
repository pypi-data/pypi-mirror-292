from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationMemberRoleProto(_message.Message):
    __slots__ = ("id", "organization_id", "user_id", "project_ids", "organization_member_id", "has_organization_level_project_access")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    HAS_ORGANIZATION_LEVEL_PROJECT_ACCESS_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    user_id: str
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    organization_member_id: str
    has_organization_level_project_access: str
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., user_id: _Optional[str] = ..., project_ids: _Optional[_Iterable[str]] = ..., organization_member_id: _Optional[str] = ..., has_organization_level_project_access: _Optional[str] = ...) -> None: ...

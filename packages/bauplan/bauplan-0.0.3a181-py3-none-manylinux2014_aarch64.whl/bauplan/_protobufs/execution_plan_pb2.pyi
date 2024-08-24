from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[JobStatus]
    PENDING: _ClassVar[JobStatus]
    RUNNING: _ClassVar[JobStatus]
    COMPLETED: _ClassVar[JobStatus]
    FAILED: _ClassVar[JobStatus]
    CANCELED: _ClassVar[JobStatus]

UNKNOWN: JobStatus
PENDING: JobStatus
RUNNING: JobStatus
COMPLETED: JobStatus
FAILED: JobStatus
CANCELED: JobStatus

class JobRequest(_message.Message):
    __slots__ = (
        'detach',
        'args',
        'status',
        'scheduled_runner_id',
        'physical_plan_v2',
        'scheduling_error',
        'user',
        'created_at',
        'finished_at',
        'read_branch',
        'write_branch',
        'tags',
    )
    class ArgsEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    class TagsEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    DETACH_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_RUNNER_ID_FIELD_NUMBER: _ClassVar[int]
    PHYSICAL_PLAN_V2_FIELD_NUMBER: _ClassVar[int]
    SCHEDULING_ERROR_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    READ_BRANCH_FIELD_NUMBER: _ClassVar[int]
    WRITE_BRANCH_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    detach: bool
    args: _containers.ScalarMap[str, str]
    status: JobStatus
    scheduled_runner_id: str
    physical_plan_v2: bytes
    scheduling_error: str
    user: str
    created_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    read_branch: str
    write_branch: str
    tags: _containers.ScalarMap[str, str]
    def __init__(
        self,
        detach: bool = ...,
        args: _Optional[_Mapping[str, str]] = ...,
        status: _Optional[_Union[JobStatus, str]] = ...,
        scheduled_runner_id: _Optional[str] = ...,
        physical_plan_v2: _Optional[bytes] = ...,
        scheduling_error: _Optional[str] = ...,
        user: _Optional[str] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        finished_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        read_branch: _Optional[str] = ...,
        write_branch: _Optional[str] = ...,
        tags: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

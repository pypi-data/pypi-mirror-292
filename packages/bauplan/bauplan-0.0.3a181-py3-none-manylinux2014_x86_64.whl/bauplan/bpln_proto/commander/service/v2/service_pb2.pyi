from bauplan.bpln_proto.commander.service.v2 import runner_events_pb2 as _runner_events_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class TriggerRunOpts(_message.Message):
    __slots__ = ('cache',)
    CACHE_FIELD_NUMBER: _ClassVar[int]
    cache: bool
    def __init__(self, cache: bool = ...) -> None: ...

class CodeIntelligenceError(_message.Message):
    __slots__ = ('type', 'message', 'traceback')
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRACEBACK_FIELD_NUMBER: _ClassVar[int]
    type: str
    message: str
    traceback: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        type: _Optional[str] = ...,
        message: _Optional[str] = ...,
        traceback: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class CodeIntelligenceResponseMetadata(_message.Message):
    __slots__ = ('status_code', 'response_id', 'response_ts')
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TS_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response_id: str
    response_ts: int
    def __init__(
        self,
        status_code: _Optional[int] = ...,
        response_id: _Optional[str] = ...,
        response_ts: _Optional[int] = ...,
    ) -> None: ...

class CreateImportPlanRequest(_message.Message):
    __slots__ = (
        'search_string',
        'max_rows',
        'trigger_run_opts',
        'args',
        'branch',
        'table',
        'append',
        'replace',
    )
    class ArgsEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    SEARCH_STRING_FIELD_NUMBER: _ClassVar[int]
    MAX_ROWS_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_RUN_OPTS_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    APPEND_FIELD_NUMBER: _ClassVar[int]
    REPLACE_FIELD_NUMBER: _ClassVar[int]
    search_string: str
    max_rows: int
    trigger_run_opts: TriggerRunOpts
    args: _containers.ScalarMap[str, str]
    branch: str
    table: str
    append: bool
    replace: bool
    def __init__(
        self,
        search_string: _Optional[str] = ...,
        max_rows: _Optional[int] = ...,
        trigger_run_opts: _Optional[_Union[TriggerRunOpts, _Mapping]] = ...,
        args: _Optional[_Mapping[str, str]] = ...,
        branch: _Optional[str] = ...,
        table: _Optional[str] = ...,
        append: bool = ...,
        replace: bool = ...,
    ) -> None: ...

class CreateImportPlanResponse(_message.Message):
    __slots__ = ('job_id',)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class ApplyImportPlanRequest(_message.Message):
    __slots__ = ('plan_yaml', 'write_branch', 'trigger_run_opts', 'args', 'merge')
    class ArgsEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    PLAN_YAML_FIELD_NUMBER: _ClassVar[int]
    WRITE_BRANCH_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_RUN_OPTS_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    MERGE_FIELD_NUMBER: _ClassVar[int]
    plan_yaml: str
    write_branch: str
    trigger_run_opts: TriggerRunOpts
    args: _containers.ScalarMap[str, str]
    merge: bool
    def __init__(
        self,
        plan_yaml: _Optional[str] = ...,
        write_branch: _Optional[str] = ...,
        trigger_run_opts: _Optional[_Union[TriggerRunOpts, _Mapping]] = ...,
        args: _Optional[_Mapping[str, str]] = ...,
        merge: bool = ...,
    ) -> None: ...

class ApplyImportPlanResponse(_message.Message):
    __slots__ = ('job_id',)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class GetJobsRequest(_message.Message):
    __slots__ = ('job_ids',)
    JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    job_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, job_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class JobInfo(_message.Message):
    __slots__ = (
        'id',
        'status',
        'kind',
        'user',
        'read_branch',
        'write_branch',
        'created_at',
        'finished_at',
        'runner',
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    READ_BRANCH_FIELD_NUMBER: _ClassVar[int]
    WRITE_BRANCH_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    RUNNER_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: str
    kind: str
    user: str
    read_branch: str
    write_branch: str
    created_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    runner: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        status: _Optional[str] = ...,
        kind: _Optional[str] = ...,
        user: _Optional[str] = ...,
        read_branch: _Optional[str] = ...,
        write_branch: _Optional[str] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        finished_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        runner: _Optional[str] = ...,
    ) -> None: ...

class GetJobsResponse(_message.Message):
    __slots__ = ('jobs',)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[JobInfo]
    def __init__(self, jobs: _Optional[_Iterable[_Union[JobInfo, _Mapping]]] = ...) -> None: ...

class GetLogsRequest(_message.Message):
    __slots__ = ('job_id', 'start', 'end', 'limit')
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    start: int
    end: int
    limit: int
    def __init__(
        self,
        job_id: _Optional[str] = ...,
        start: _Optional[int] = ...,
        end: _Optional[int] = ...,
        limit: _Optional[int] = ...,
    ) -> None: ...

class GetLogsResponse(_message.Message):
    __slots__ = ('events', 'job')
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    JOB_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[_runner_events_pb2.RunnerEvent]
    job: JobInfo
    def __init__(
        self,
        events: _Optional[_Iterable[_Union[_runner_events_pb2.RunnerEvent, _Mapping]]] = ...,
        job: _Optional[_Union[JobInfo, _Mapping]] = ...,
    ) -> None: ...

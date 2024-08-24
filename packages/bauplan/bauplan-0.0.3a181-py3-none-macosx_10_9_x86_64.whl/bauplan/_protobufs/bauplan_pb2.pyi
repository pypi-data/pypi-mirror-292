import commander_pb2 as _commander_pb2
import execution_plan_pb2 as _execution_plan_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)
from execution_plan_pb2 import JobRequest as JobRequest
from execution_plan_pb2 import JobStatus as JobStatus

DESCRIPTOR: _descriptor.FileDescriptor
UNKNOWN: _execution_plan_pb2.JobStatus
PENDING: _execution_plan_pb2.JobStatus
RUNNING: _execution_plan_pb2.JobStatus
COMPLETED: _execution_plan_pb2.JobStatus
FAILED: _execution_plan_pb2.JobStatus
CANCELED: _execution_plan_pb2.JobStatus

class AllocationStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISK: _ClassVar[AllocationStrategy]
    SHMEM: _ClassVar[AllocationStrategy]

DISK: AllocationStrategy
SHMEM: AllocationStrategy

class MemoryRelease(_message.Message):
    __slots__ = ('id', 'input_object')
    ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    id: str
    input_object: str
    def __init__(self, id: _Optional[str] = ..., input_object: _Optional[str] = ...) -> None: ...

class JobId(_message.Message):
    __slots__ = ('id', 'snapshot_key', 'dag_graphviz', 'dag_ascii', 'scheduled_runner_id')
    ID_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_KEY_FIELD_NUMBER: _ClassVar[int]
    DAG_GRAPHVIZ_FIELD_NUMBER: _ClassVar[int]
    DAG_ASCII_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_RUNNER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    snapshot_key: str
    dag_graphviz: str
    dag_ascii: str
    scheduled_runner_id: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        snapshot_key: _Optional[str] = ...,
        dag_graphviz: _Optional[str] = ...,
        dag_ascii: _Optional[str] = ...,
        scheduled_runner_id: _Optional[str] = ...,
    ) -> None: ...

class JobResult(_message.Message):
    __slots__ = ('job_id', 'result_data', 'error')
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    result_data: str
    error: str
    def __init__(
        self,
        job_id: _Optional[_Union[JobId, _Mapping]] = ...,
        result_data: _Optional[str] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...

class CancelJobRequest(_message.Message):
    __slots__ = ('job_id',)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    def __init__(self, job_id: _Optional[_Union[JobId, _Mapping]] = ...) -> None: ...

class CancelJobResponse(_message.Message):
    __slots__ = ('status', 'message')
    class CancelStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[CancelJobResponse.CancelStatus]
        FAILURE: _ClassVar[CancelJobResponse.CancelStatus]

    SUCCESS: CancelJobResponse.CancelStatus
    FAILURE: CancelJobResponse.CancelStatus
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: CancelJobResponse.CancelStatus
    message: str
    def __init__(
        self,
        status: _Optional[_Union[CancelJobResponse.CancelStatus, str]] = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class RunnerAction(_message.Message):
    __slots__ = ('job_id', 'action', 'job_request', 'trace_id', 'parent_span_id', 'job_args')
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        START: _ClassVar[RunnerAction.Action]
        CANCEL: _ClassVar[RunnerAction.Action]
        UPLOAD: _ClassVar[RunnerAction.Action]
        QUERY: _ClassVar[RunnerAction.Action]

    START: RunnerAction.Action
    CANCEL: RunnerAction.Action
    UPLOAD: RunnerAction.Action
    QUERY: RunnerAction.Action
    class JobArgsEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    JOB_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ARGS_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    action: RunnerAction.Action
    job_request: _execution_plan_pb2.JobRequest
    trace_id: str
    parent_span_id: str
    job_args: _containers.ScalarMap[str, str]
    def __init__(
        self,
        job_id: _Optional[_Union[JobId, _Mapping]] = ...,
        action: _Optional[_Union[RunnerAction.Action, str]] = ...,
        job_request: _Optional[_Union[_execution_plan_pb2.JobRequest, _Mapping]] = ...,
        trace_id: _Optional[str] = ...,
        parent_span_id: _Optional[str] = ...,
        job_args: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class RunnerInfo(_message.Message):
    __slots__ = ('job_id', 'runner_event')
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_EVENT_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    runner_event: _commander_pb2.RunnerEvent
    def __init__(
        self,
        job_id: _Optional[_Union[JobId, _Mapping]] = ...,
        runner_event: _Optional[_Union[_commander_pb2.RunnerEvent, _Mapping]] = ...,
    ) -> None: ...

class RunnerLabel(_message.Message):
    __slots__ = ('key', 'value')
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class NodeInfo(_message.Message):
    __slots__ = ('nodes',)
    NODES_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    def __init__(self, nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ('id', 'public_key', 'hostname', 'resources', 'labels')
    ID_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: str
    public_key: str
    hostname: str
    resources: Resources
    labels: _containers.RepeatedCompositeFieldContainer[RunnerLabel]
    def __init__(
        self,
        id: _Optional[str] = ...,
        public_key: _Optional[str] = ...,
        hostname: _Optional[str] = ...,
        resources: _Optional[_Union[Resources, _Mapping]] = ...,
        labels: _Optional[_Iterable[_Union[RunnerLabel, _Mapping]]] = ...,
    ) -> None: ...

class Resources(_message.Message):
    __slots__ = ('cpus', 'memory_bytes', 'disk_space_bytes', 'client_version')
    CPUS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    DISK_SPACE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    cpus: int
    memory_bytes: int
    disk_space_bytes: int
    client_version: str
    def __init__(
        self,
        cpus: _Optional[int] = ...,
        memory_bytes: _Optional[int] = ...,
        disk_space_bytes: _Optional[int] = ...,
        client_version: _Optional[str] = ...,
    ) -> None: ...

class ColumnInfo(_message.Message):
    __slots__ = (
        'name',
        'type',
        'nulls',
        'compression',
        'encoding',
        'min',
        'max',
        'distinct_count',
        'total_rows',
        'num_values',
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NULLS_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    DISTINCT_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    NUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    nulls: int
    compression: str
    encoding: str
    min: str
    max: str
    distinct_count: int
    total_rows: int
    num_values: int
    def __init__(
        self,
        name: _Optional[str] = ...,
        type: _Optional[str] = ...,
        nulls: _Optional[int] = ...,
        compression: _Optional[str] = ...,
        encoding: _Optional[str] = ...,
        min: _Optional[str] = ...,
        max: _Optional[str] = ...,
        distinct_count: _Optional[int] = ...,
        total_rows: _Optional[int] = ...,
        num_values: _Optional[int] = ...,
    ) -> None: ...

class BranchInfo(_message.Message):
    __slots__ = ('table', 'branch', 'snapshotted_at', 'active')
    TABLE_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOTTED_AT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    table: str
    branch: str
    snapshotted_at: _timestamp_pb2.Timestamp
    active: bool
    def __init__(
        self,
        table: _Optional[str] = ...,
        branch: _Optional[str] = ...,
        snapshotted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        active: bool = ...,
    ) -> None: ...

class TriggerRunRequest(_message.Message):
    __slots__ = (
        'zip_file',
        'module_version',
        'allocation_strategy',
        'client_hostname',
        'args',
        'is_flight_query',
        'query_for_flight',
        'run_id',
        'cache',
    )
    class ArgsEntry(_message.Message):
        __slots__ = ('key', 'value')
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    ZIP_FILE_FIELD_NUMBER: _ClassVar[int]
    MODULE_VERSION_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    IS_FLIGHT_QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_FOR_FLIGHT_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    CACHE_FIELD_NUMBER: _ClassVar[int]
    zip_file: bytes
    module_version: str
    allocation_strategy: AllocationStrategy
    client_hostname: str
    args: _containers.ScalarMap[str, str]
    is_flight_query: bool
    query_for_flight: str
    run_id: str
    cache: bool
    def __init__(
        self,
        zip_file: _Optional[bytes] = ...,
        module_version: _Optional[str] = ...,
        allocation_strategy: _Optional[_Union[AllocationStrategy, str]] = ...,
        client_hostname: _Optional[str] = ...,
        args: _Optional[_Mapping[str, str]] = ...,
        is_flight_query: bool = ...,
        query_for_flight: _Optional[str] = ...,
        run_id: _Optional[str] = ...,
        cache: bool = ...,
    ) -> None: ...

class AccountMetadata(_message.Message):
    __slots__ = ('username',)
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

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

class User(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Account(_message.Message):
    __slots__ = ('api_key', 'email', 'full_name', 'enabled', 'username', 'is_admin', 'nessie_host', 'runners')
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    IS_ADMIN_FIELD_NUMBER: _ClassVar[int]
    NESSIE_HOST_FIELD_NUMBER: _ClassVar[int]
    RUNNERS_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    email: str
    full_name: str
    enabled: bool
    username: str
    is_admin: bool
    nessie_host: str
    runners: str
    def __init__(
        self,
        api_key: _Optional[str] = ...,
        email: _Optional[str] = ...,
        full_name: _Optional[str] = ...,
        enabled: bool = ...,
        username: _Optional[str] = ...,
        is_admin: bool = ...,
        nessie_host: _Optional[str] = ...,
        runners: _Optional[str] = ...,
    ) -> None: ...

class SyncAlphaAccountsRequest(_message.Message):
    __slots__ = ('accounts', 'magic_token')
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    MAGIC_TOKEN_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[Account]
    magic_token: str
    def __init__(
        self,
        accounts: _Optional[_Iterable[_Union[Account, _Mapping]]] = ...,
        magic_token: _Optional[str] = ...,
    ) -> None: ...

class SyncAlphaAccountsResponse(_message.Message):
    __slots__ = ('error',)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class GetSnapshotInfoRequest(_message.Message):
    __slots__ = ('snapshot_sha',)
    SNAPSHOT_SHA_FIELD_NUMBER: _ClassVar[int]
    snapshot_sha: str
    def __init__(self, snapshot_sha: _Optional[str] = ...) -> None: ...

class GetSnapshotInfoResponse(_message.Message):
    __slots__ = ('snapshot_info',)
    SNAPSHOT_INFO_FIELD_NUMBER: _ClassVar[int]
    snapshot_info: SnapshotInfo
    def __init__(self, snapshot_info: _Optional[_Union[SnapshotInfo, _Mapping]] = ...) -> None: ...

class SnapshotInfo(_message.Message):
    __slots__ = ('snapshot_zip', 'created_at')
    SNAPSHOT_ZIP_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    snapshot_zip: bytes
    created_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        snapshot_zip: _Optional[bytes] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class BauplanInfoRequest(_message.Message):
    __slots__ = ('api_key',)
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    def __init__(self, api_key: _Optional[str] = ...) -> None: ...

class RunnerNodeInfo(_message.Message):
    __slots__ = ('public_key', 'hostname', 'resources', 'labels')
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    public_key: str
    hostname: str
    resources: Resources
    labels: _containers.RepeatedCompositeFieldContainer[RunnerLabel]
    def __init__(
        self,
        public_key: _Optional[str] = ...,
        hostname: _Optional[str] = ...,
        resources: _Optional[_Union[Resources, _Mapping]] = ...,
        labels: _Optional[_Iterable[_Union[RunnerLabel, _Mapping]]] = ...,
    ) -> None: ...

class BauplanInfo(_message.Message):
    __slots__ = ('runners', 'user', 'client_version', 'server_version')
    RUNNERS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    runners: _containers.RepeatedCompositeFieldContainer[RunnerNodeInfo]
    user: str
    client_version: str
    server_version: str
    def __init__(
        self,
        runners: _Optional[_Iterable[_Union[RunnerNodeInfo, _Mapping]]] = ...,
        user: _Optional[str] = ...,
        client_version: _Optional[str] = ...,
        server_version: _Optional[str] = ...,
    ) -> None: ...

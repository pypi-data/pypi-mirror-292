from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskMetadata(_message.Message):
    __slots__ = (
        'level',
        'human_readable_task_type',
        'task_type',
        'function_name',
        'line_number',
        'file_name',
        'model_name',
    )
    class TaskLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DAG: _ClassVar[TaskMetadata.TaskLevel]
        SYSTEM: _ClassVar[TaskMetadata.TaskLevel]

    DAG: TaskMetadata.TaskLevel
    SYSTEM: TaskMetadata.TaskLevel
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    HUMAN_READABLE_TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    level: TaskMetadata.TaskLevel
    human_readable_task_type: str
    task_type: str
    function_name: str
    line_number: int
    file_name: str
    model_name: str
    def __init__(
        self,
        level: _Optional[_Union[TaskMetadata.TaskLevel, str]] = ...,
        human_readable_task_type: _Optional[str] = ...,
        task_type: _Optional[str] = ...,
        function_name: _Optional[str] = ...,
        line_number: _Optional[int] = ...,
        file_name: _Optional[str] = ...,
        model_name: _Optional[str] = ...,
    ) -> None: ...

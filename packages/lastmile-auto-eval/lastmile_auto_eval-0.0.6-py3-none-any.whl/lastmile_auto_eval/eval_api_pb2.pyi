from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StringList(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class ModelSpecifier(_message.Message):
    __slots__ = ("identifier", "version")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    identifier: str
    version: str
    def __init__(self, identifier: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class RequestBody(_message.Message):
    __slots__ = ("input", "ground_truth", "context", "output", "model_specifiers")
    INPUT_FIELD_NUMBER: _ClassVar[int]
    GROUND_TRUTH_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    MODEL_SPECIFIERS_FIELD_NUMBER: _ClassVar[int]
    input: StringList
    ground_truth: StringList
    context: StringList
    output: StringList
    model_specifiers: _containers.RepeatedCompositeFieldContainer[ModelSpecifier]
    def __init__(self, input: _Optional[_Union[StringList, _Mapping]] = ..., ground_truth: _Optional[_Union[StringList, _Mapping]] = ..., context: _Optional[_Union[StringList, _Mapping]] = ..., output: _Optional[_Union[StringList, _Mapping]] = ..., model_specifiers: _Optional[_Iterable[_Union[ModelSpecifier, _Mapping]]] = ...) -> None: ...

class FloatList(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("scores",)
    class ScoresEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FloatList
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FloatList, _Mapping]] = ...) -> None: ...
    SCORES_FIELD_NUMBER: _ClassVar[int]
    scores: _containers.MessageMap[str, FloatList]
    def __init__(self, scores: _Optional[_Mapping[str, FloatList]] = ...) -> None: ...

class Job(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

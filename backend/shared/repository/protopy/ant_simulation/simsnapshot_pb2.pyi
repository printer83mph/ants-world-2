from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SimSnapshot(_message.Message):
    __slots__ = ("created_at", "ant_ids", "ants", "pheremones", "crumbs")
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ANT_IDS_FIELD_NUMBER: _ClassVar[int]
    ANTS_FIELD_NUMBER: _ClassVar[int]
    PHEREMONES_FIELD_NUMBER: _ClassVar[int]
    CRUMBS_FIELD_NUMBER: _ClassVar[int]
    created_at: int
    ant_ids: _containers.RepeatedScalarFieldContainer[bytes]
    ants: _containers.RepeatedCompositeFieldContainer[AntState]
    pheremones: _containers.RepeatedCompositeFieldContainer[PheremoneState]
    crumbs: _containers.RepeatedCompositeFieldContainer[CrumbState]
    def __init__(self, created_at: _Optional[int] = ..., ant_ids: _Optional[_Iterable[bytes]] = ..., ants: _Optional[_Iterable[_Union[AntState, _Mapping]]] = ..., pheremones: _Optional[_Iterable[_Union[PheremoneState, _Mapping]]] = ..., crumbs: _Optional[_Iterable[_Union[CrumbState, _Mapping]]] = ...) -> None: ...

class AntState(_message.Message):
    __slots__ = ("x", "y", "rotation", "pheremone_sensitivity", "pheremone_strength", "speed", "seconds_of_life_left")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    PHEREMONE_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    PHEREMONE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    SECONDS_OF_LIFE_LEFT_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    rotation: float
    pheremone_sensitivity: float
    pheremone_strength: float
    speed: float
    seconds_of_life_left: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., rotation: _Optional[float] = ..., pheremone_sensitivity: _Optional[float] = ..., pheremone_strength: _Optional[float] = ..., speed: _Optional[float] = ..., seconds_of_life_left: _Optional[float] = ...) -> None: ...

class PheremoneState(_message.Message):
    __slots__ = ("x", "y", "is_leaving_home", "seconds_of_life_left")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    IS_LEAVING_HOME_FIELD_NUMBER: _ClassVar[int]
    SECONDS_OF_LIFE_LEFT_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    is_leaving_home: bool
    seconds_of_life_left: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., is_leaving_home: _Optional[bool] = ..., seconds_of_life_left: _Optional[float] = ...) -> None: ...

class CrumbState(_message.Message):
    __slots__ = ("x", "y", "size")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    size: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., size: _Optional[float] = ...) -> None: ...

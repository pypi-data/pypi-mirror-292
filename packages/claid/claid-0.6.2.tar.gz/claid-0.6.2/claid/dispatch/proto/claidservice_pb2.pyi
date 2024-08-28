from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CtrlType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CTRL_UNSPECIFIED: _ClassVar[CtrlType]
    CTRL_RUNTIME_PING: _ClassVar[CtrlType]
    CTRL_REMOTE_PING: _ClassVar[CtrlType]
    CTRL_REMOTE_PING_PONG: _ClassVar[CtrlType]
    CTRL_CONN_CANCEL: _ClassVar[CtrlType]
    CTRL_ERROR: _ClassVar[CtrlType]
    CTRL_CONNECTED_TO_REMOTE_SERVER: _ClassVar[CtrlType]
    CTRL_DISCONNECTED_FROM_REMOTE_SERVER: _ClassVar[CtrlType]
    CTRL_UNLOAD_MODULES: _ClassVar[CtrlType]
    CTRL_UNLOAD_MODULES_DONE: _ClassVar[CtrlType]
    CTRL_RESTART_RUNTIME: _ClassVar[CtrlType]
    CTRL_RESTART_RUNTIME_DONE: _ClassVar[CtrlType]
    CTRL_STOP_RUNTIME: _ClassVar[CtrlType]
    CTRL_REQUEST_MODULE_ANNOTATIONS: _ClassVar[CtrlType]
    CTRL_REQUEST_MODULE_ANNOTATIONS_RESPONSE: _ClassVar[CtrlType]
    CTRL_UPLOAD_CONFIG_AND_DATA: _ClassVar[CtrlType]
    CTRL_ON_NEW_CONFIG_PAYLOAD_DATA: _ClassVar[CtrlType]
    CTRL_LOCAL_LOG_MESSAGE: _ClassVar[CtrlType]
    CTRL_LOG_SINK_LOG_MESSAGE_STREAM: _ClassVar[CtrlType]
    CTRL_SUBSCRIBE_TO_LOG_SINK_LOG_MESSAGE_STREAM: _ClassVar[CtrlType]
    CTRL_UNSUBSCRIBE_FROM_LOG_SINK_LOG_MESSAGE_STREAM: _ClassVar[CtrlType]
    CTRL_PAUSE_MODULE: _ClassVar[CtrlType]
    CTRL_UNPAUSE_MODULE: _ClassVar[CtrlType]
    CTRL_ADJUST_POWER_PROFILE: _ClassVar[CtrlType]
    CTRL_ACTIVATE_NETWORK_CONNECTIONS: _ClassVar[CtrlType]
    CTRL_DEACTIVATE_NETWORK_CONNECTIONS: _ClassVar[CtrlType]
    CTRL_REMOTE_FUNCTION_REQUEST: _ClassVar[CtrlType]
    CTRL_REMOTE_FUNCTION_RESPONSE: _ClassVar[CtrlType]
    CTRL_DIRECT_SUBSCRIPTION_DATA: _ClassVar[CtrlType]

class Codec(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CODEC_UNSPECIFIED: _ClassVar[Codec]
    CODEC_BYTES: _ClassVar[Codec]
    CODEC_FILE: _ClassVar[Codec]
    CODEC_JSON: _ClassVar[Codec]
    CODEC_PROTO: _ClassVar[Codec]

class PropertyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    PROPERTY_TYPE_DEFAULT: _ClassVar[PropertyType]
    PROPERTY_TYPE_ENUM: _ClassVar[PropertyType]
    PROPERTY_TYPE_INT: _ClassVar[PropertyType]
    PROPERTY_TYPE_PATH: _ClassVar[PropertyType]

class Runtime(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RUNTIME_UNSPECIFIED: _ClassVar[Runtime]
    MIDDLEWARE_CORE: _ClassVar[Runtime]
    RUNTIME_CPP: _ClassVar[Runtime]
    RUNTIME_DART: _ClassVar[Runtime]
    RUNTIME_JAVA: _ClassVar[Runtime]
    RUNTIME_PYTHON: _ClassVar[Runtime]

class LogMessageSeverityLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DEBUG_VERBOSE: _ClassVar[LogMessageSeverityLevel]
    INFO: _ClassVar[LogMessageSeverityLevel]
    WARNING: _ClassVar[LogMessageSeverityLevel]
    ERROR: _ClassVar[LogMessageSeverityLevel]
    FATAL: _ClassVar[LogMessageSeverityLevel]

class LogMessageEntityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    MIDDLEWARE: _ClassVar[LogMessageEntityType]
    MIDDLEWARE_COMPONENT: _ClassVar[LogMessageEntityType]
    MODULE: _ClassVar[LogMessageEntityType]

class LogSinkTransferMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    STORE_AND_UPLOAD: _ClassVar[LogSinkTransferMode]
    STREAM: _ClassVar[LogSinkTransferMode]

class PowerProfileType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNRESTRICTED: _ClassVar[PowerProfileType]
    POWER_SAVING_MODE: _ClassVar[PowerProfileType]

class RemoteFunctionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNDEFINED: _ClassVar[RemoteFunctionStatus]
    STATUS_OK: _ClassVar[RemoteFunctionStatus]
    FAILED_FUNCTION_NOT_FOUND_OR_FAILED_TO_EXECUTE: _ClassVar[RemoteFunctionStatus]
    FAILED_INVALID_NUMBER_OF_PARAMETERS: _ClassVar[RemoteFunctionStatus]
    FAILED_MISMATCHING_PARAMETERS: _ClassVar[RemoteFunctionStatus]
    FAILED_MODULE_NOT_FOUND: _ClassVar[RemoteFunctionStatus]
    REMOTE_FUNCTION_REQUEST_INVALID: _ClassVar[RemoteFunctionStatus]

class DataSyncPackageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ALL_AVAILABLE_FILES_LIST: _ClassVar[DataSyncPackageType]
    REQUESTED_FILES_LIST: _ClassVar[DataSyncPackageType]
    FILES_DATA: _ClassVar[DataSyncPackageType]
    ACKNOWLEDGED_FILES: _ClassVar[DataSyncPackageType]
CTRL_UNSPECIFIED: CtrlType
CTRL_RUNTIME_PING: CtrlType
CTRL_REMOTE_PING: CtrlType
CTRL_REMOTE_PING_PONG: CtrlType
CTRL_CONN_CANCEL: CtrlType
CTRL_ERROR: CtrlType
CTRL_CONNECTED_TO_REMOTE_SERVER: CtrlType
CTRL_DISCONNECTED_FROM_REMOTE_SERVER: CtrlType
CTRL_UNLOAD_MODULES: CtrlType
CTRL_UNLOAD_MODULES_DONE: CtrlType
CTRL_RESTART_RUNTIME: CtrlType
CTRL_RESTART_RUNTIME_DONE: CtrlType
CTRL_STOP_RUNTIME: CtrlType
CTRL_REQUEST_MODULE_ANNOTATIONS: CtrlType
CTRL_REQUEST_MODULE_ANNOTATIONS_RESPONSE: CtrlType
CTRL_UPLOAD_CONFIG_AND_DATA: CtrlType
CTRL_ON_NEW_CONFIG_PAYLOAD_DATA: CtrlType
CTRL_LOCAL_LOG_MESSAGE: CtrlType
CTRL_LOG_SINK_LOG_MESSAGE_STREAM: CtrlType
CTRL_SUBSCRIBE_TO_LOG_SINK_LOG_MESSAGE_STREAM: CtrlType
CTRL_UNSUBSCRIBE_FROM_LOG_SINK_LOG_MESSAGE_STREAM: CtrlType
CTRL_PAUSE_MODULE: CtrlType
CTRL_UNPAUSE_MODULE: CtrlType
CTRL_ADJUST_POWER_PROFILE: CtrlType
CTRL_ACTIVATE_NETWORK_CONNECTIONS: CtrlType
CTRL_DEACTIVATE_NETWORK_CONNECTIONS: CtrlType
CTRL_REMOTE_FUNCTION_REQUEST: CtrlType
CTRL_REMOTE_FUNCTION_RESPONSE: CtrlType
CTRL_DIRECT_SUBSCRIPTION_DATA: CtrlType
CODEC_UNSPECIFIED: Codec
CODEC_BYTES: Codec
CODEC_FILE: Codec
CODEC_JSON: Codec
CODEC_PROTO: Codec
PROPERTY_TYPE_DEFAULT: PropertyType
PROPERTY_TYPE_ENUM: PropertyType
PROPERTY_TYPE_INT: PropertyType
PROPERTY_TYPE_PATH: PropertyType
RUNTIME_UNSPECIFIED: Runtime
MIDDLEWARE_CORE: Runtime
RUNTIME_CPP: Runtime
RUNTIME_DART: Runtime
RUNTIME_JAVA: Runtime
RUNTIME_PYTHON: Runtime
DEBUG_VERBOSE: LogMessageSeverityLevel
INFO: LogMessageSeverityLevel
WARNING: LogMessageSeverityLevel
ERROR: LogMessageSeverityLevel
FATAL: LogMessageSeverityLevel
MIDDLEWARE: LogMessageEntityType
MIDDLEWARE_COMPONENT: LogMessageEntityType
MODULE: LogMessageEntityType
STORE_AND_UPLOAD: LogSinkTransferMode
STREAM: LogSinkTransferMode
UNRESTRICTED: PowerProfileType
POWER_SAVING_MODE: PowerProfileType
UNDEFINED: RemoteFunctionStatus
STATUS_OK: RemoteFunctionStatus
FAILED_FUNCTION_NOT_FOUND_OR_FAILED_TO_EXECUTE: RemoteFunctionStatus
FAILED_INVALID_NUMBER_OF_PARAMETERS: RemoteFunctionStatus
FAILED_MISMATCHING_PARAMETERS: RemoteFunctionStatus
FAILED_MODULE_NOT_FOUND: RemoteFunctionStatus
REMOTE_FUNCTION_REQUEST_INVALID: RemoteFunctionStatus
ALL_AVAILABLE_FILES_LIST: DataSyncPackageType
REQUESTED_FILES_LIST: DataSyncPackageType
FILES_DATA: DataSyncPackageType
ACKNOWLEDGED_FILES: DataSyncPackageType

class DataPackage(_message.Message):
    __slots__ = ["id", "channel", "source_module", "target_module", "source_host", "target_host", "source_user_token", "target_user_token", "device_id", "trace_points", "unix_timestamp_ms", "payload", "control_val"]
    ID_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    SOURCE_MODULE_FIELD_NUMBER: _ClassVar[int]
    TARGET_MODULE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_HOST_FIELD_NUMBER: _ClassVar[int]
    TARGET_HOST_FIELD_NUMBER: _ClassVar[int]
    SOURCE_USER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TARGET_USER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_POINTS_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    CONTROL_VAL_FIELD_NUMBER: _ClassVar[int]
    id: str
    channel: str
    source_module: str
    target_module: str
    source_host: str
    target_host: str
    source_user_token: str
    target_user_token: str
    device_id: str
    trace_points: _containers.RepeatedCompositeFieldContainer[TracePoint]
    unix_timestamp_ms: int
    payload: Blob
    control_val: ControlPackage
    def __init__(self, id: _Optional[str] = ..., channel: _Optional[str] = ..., source_module: _Optional[str] = ..., target_module: _Optional[str] = ..., source_host: _Optional[str] = ..., target_host: _Optional[str] = ..., source_user_token: _Optional[str] = ..., target_user_token: _Optional[str] = ..., device_id: _Optional[str] = ..., trace_points: _Optional[_Iterable[_Union[TracePoint, _Mapping]]] = ..., unix_timestamp_ms: _Optional[int] = ..., payload: _Optional[_Union[Blob, _Mapping]] = ..., control_val: _Optional[_Union[ControlPackage, _Mapping]] = ...) -> None: ...

class ControlPackage(_message.Message):
    __slots__ = ["ctrl_type", "runtime", "remote_client_info", "status", "error_msg", "action_request", "module_annotations", "config_upload_payload", "log_message", "power_profile", "remote_function_request", "remote_function_return", "loose_direct_subscription"]
    class ModuleAnnotationsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ModuleAnnotation
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ModuleAnnotation, _Mapping]] = ...) -> None: ...
    CTRL_TYPE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    REMOTE_CLIENT_INFO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    ACTION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    MODULE_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_UPLOAD_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    LOG_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    POWER_PROFILE_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FUNCTION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FUNCTION_RETURN_FIELD_NUMBER: _ClassVar[int]
    LOOSE_DIRECT_SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ctrl_type: CtrlType
    runtime: Runtime
    remote_client_info: RemoteClientInfo
    status: AccumulatedStatus
    error_msg: ErrorMsg
    action_request: ActionRequest
    module_annotations: _containers.MessageMap[str, ModuleAnnotation]
    config_upload_payload: ConfigUploadPayload
    log_message: LogMessage
    power_profile: PowerProfile
    remote_function_request: RemoteFunctionRequest
    remote_function_return: RemoteFunctionReturn
    loose_direct_subscription: LooseDirectChannelSubscription
    def __init__(self, ctrl_type: _Optional[_Union[CtrlType, str]] = ..., runtime: _Optional[_Union[Runtime, str]] = ..., remote_client_info: _Optional[_Union[RemoteClientInfo, _Mapping]] = ..., status: _Optional[_Union[AccumulatedStatus, _Mapping]] = ..., error_msg: _Optional[_Union[ErrorMsg, _Mapping]] = ..., action_request: _Optional[_Union[ActionRequest, _Mapping]] = ..., module_annotations: _Optional[_Mapping[str, ModuleAnnotation]] = ..., config_upload_payload: _Optional[_Union[ConfigUploadPayload, _Mapping]] = ..., log_message: _Optional[_Union[LogMessage, _Mapping]] = ..., power_profile: _Optional[_Union[PowerProfile, _Mapping]] = ..., remote_function_request: _Optional[_Union[RemoteFunctionRequest, _Mapping]] = ..., remote_function_return: _Optional[_Union[RemoteFunctionReturn, _Mapping]] = ..., loose_direct_subscription: _Optional[_Union[LooseDirectChannelSubscription, _Mapping]] = ...) -> None: ...

class AccumulatedStatus(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ErrorMsg(_message.Message):
    __slots__ = ["message", "cancel"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    message: str
    cancel: bool
    def __init__(self, message: _Optional[str] = ..., cancel: bool = ...) -> None: ...

class ActionRequest(_message.Message):
    __slots__ = ["action_params"]
    class ActionParamsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ACTION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    action_params: _containers.ScalarMap[str, str]
    def __init__(self, action_params: _Optional[_Mapping[str, str]] = ...) -> None: ...

class IntVal(_message.Message):
    __slots__ = ["val"]
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: int
    def __init__(self, val: _Optional[int] = ...) -> None: ...

class DoubleVal(_message.Message):
    __slots__ = ["val"]
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: float
    def __init__(self, val: _Optional[float] = ...) -> None: ...

class NumberArray(_message.Message):
    __slots__ = ["val"]
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, val: _Optional[_Iterable[float]] = ...) -> None: ...

class BoolVal(_message.Message):
    __slots__ = ["val"]
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: bool
    def __init__(self, val: bool = ...) -> None: ...

class StringVal(_message.Message):
    __slots__ = ["val"]
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: str
    def __init__(self, val: _Optional[str] = ...) -> None: ...

class StringArray(_message.Message):
    __slots__ = ["val"]
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, val: _Optional[_Iterable[str]] = ...) -> None: ...

class NumberMap(_message.Message):
    __slots__ = ["val"]
    class ValEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: _containers.ScalarMap[str, float]
    def __init__(self, val: _Optional[_Mapping[str, float]] = ...) -> None: ...

class StringMap(_message.Message):
    __slots__ = ["val"]
    class ValEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: _containers.ScalarMap[str, str]
    def __init__(self, val: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Blob(_message.Message):
    __slots__ = ["codec", "payload", "message_type"]
    CODEC_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    codec: Codec
    payload: bytes
    message_type: str
    def __init__(self, codec: _Optional[_Union[Codec, str]] = ..., payload: _Optional[bytes] = ..., message_type: _Optional[str] = ...) -> None: ...

class TracePoint(_message.Message):
    __slots__ = ["time_stamp", "node_id"]
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    time_stamp: _timestamp_pb2.Timestamp
    node_id: str
    def __init__(self, time_stamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., node_id: _Optional[str] = ...) -> None: ...

class ModuleListRequest(_message.Message):
    __slots__ = ["runtime", "supported_module_classes", "module_annotations"]
    class ModuleAnnotationsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ModuleAnnotation
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ModuleAnnotation, _Mapping]] = ...) -> None: ...
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_MODULE_CLASSES_FIELD_NUMBER: _ClassVar[int]
    MODULE_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    runtime: Runtime
    supported_module_classes: _containers.RepeatedScalarFieldContainer[str]
    module_annotations: _containers.MessageMap[str, ModuleAnnotation]
    def __init__(self, runtime: _Optional[_Union[Runtime, str]] = ..., supported_module_classes: _Optional[_Iterable[str]] = ..., module_annotations: _Optional[_Mapping[str, ModuleAnnotation]] = ...) -> None: ...

class ModuleListResponse(_message.Message):
    __slots__ = ["descriptors", "log_severity_level_for_host"]
    class ModuleDescriptor(_message.Message):
        __slots__ = ["module_id", "module_class", "properties"]
        MODULE_ID_FIELD_NUMBER: _ClassVar[int]
        MODULE_CLASS_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        module_id: str
        module_class: str
        properties: _struct_pb2.Struct
        def __init__(self, module_id: _Optional[str] = ..., module_class: _Optional[str] = ..., properties: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
    DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    LOG_SEVERITY_LEVEL_FOR_HOST_FIELD_NUMBER: _ClassVar[int]
    descriptors: _containers.RepeatedCompositeFieldContainer[ModuleListResponse.ModuleDescriptor]
    log_severity_level_for_host: LogMessageSeverityLevel
    def __init__(self, descriptors: _Optional[_Iterable[_Union[ModuleListResponse.ModuleDescriptor, _Mapping]]] = ..., log_severity_level_for_host: _Optional[_Union[LogMessageSeverityLevel, str]] = ...) -> None: ...

class InitRuntimeRequest(_message.Message):
    __slots__ = ["runtime", "modules"]
    class ModuleChannels(_message.Message):
        __slots__ = ["module_id", "channel_packets"]
        MODULE_ID_FIELD_NUMBER: _ClassVar[int]
        CHANNEL_PACKETS_FIELD_NUMBER: _ClassVar[int]
        module_id: str
        channel_packets: _containers.RepeatedCompositeFieldContainer[DataPackage]
        def __init__(self, module_id: _Optional[str] = ..., channel_packets: _Optional[_Iterable[_Union[DataPackage, _Mapping]]] = ...) -> None: ...
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    MODULES_FIELD_NUMBER: _ClassVar[int]
    runtime: Runtime
    modules: _containers.RepeatedCompositeFieldContainer[InitRuntimeRequest.ModuleChannels]
    def __init__(self, runtime: _Optional[_Union[Runtime, str]] = ..., modules: _Optional[_Iterable[_Union[InitRuntimeRequest.ModuleChannels, _Mapping]]] = ...) -> None: ...

class RemoteClientInfo(_message.Message):
    __slots__ = ["host", "user_token", "device_id"]
    HOST_FIELD_NUMBER: _ClassVar[int]
    USER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    host: str
    user_token: str
    device_id: str
    def __init__(self, host: _Optional[str] = ..., user_token: _Optional[str] = ..., device_id: _Optional[str] = ...) -> None: ...

class RemoveModuleRequest(_message.Message):
    __slots__ = ["module_id"]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    module_id: str
    def __init__(self, module_id: _Optional[str] = ...) -> None: ...

class PropertyHint(_message.Message):
    __slots__ = ["property_type", "property_type_enum_values", "property_type_int_min", "property_type_int_max"]
    PROPERTY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_TYPE_ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_TYPE_INT_MIN_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_TYPE_INT_MAX_FIELD_NUMBER: _ClassVar[int]
    property_type: PropertyType
    property_type_enum_values: _containers.RepeatedScalarFieldContainer[str]
    property_type_int_min: int
    property_type_int_max: int
    def __init__(self, property_type: _Optional[_Union[PropertyType, str]] = ..., property_type_enum_values: _Optional[_Iterable[str]] = ..., property_type_int_min: _Optional[int] = ..., property_type_int_max: _Optional[int] = ...) -> None: ...

class ModuleAnnotation(_message.Message):
    __slots__ = ["module_description", "module_category", "properties", "property_descriptions", "property_hints", "channel_definition", "channel_description", "is_injectable", "file_dependencies"]
    MODULE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MODULE_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_DESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_HINTS_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_INJECTABLE_FIELD_NUMBER: _ClassVar[int]
    FILE_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    module_description: str
    module_category: str
    properties: _containers.RepeatedScalarFieldContainer[str]
    property_descriptions: _containers.RepeatedScalarFieldContainer[str]
    property_hints: _containers.RepeatedCompositeFieldContainer[PropertyHint]
    channel_definition: _containers.RepeatedCompositeFieldContainer[DataPackage]
    channel_description: _containers.RepeatedScalarFieldContainer[str]
    is_injectable: bool
    file_dependencies: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, module_description: _Optional[str] = ..., module_category: _Optional[str] = ..., properties: _Optional[_Iterable[str]] = ..., property_descriptions: _Optional[_Iterable[str]] = ..., property_hints: _Optional[_Iterable[_Union[PropertyHint, _Mapping]]] = ..., channel_definition: _Optional[_Iterable[_Union[DataPackage, _Mapping]]] = ..., channel_description: _Optional[_Iterable[str]] = ..., is_injectable: bool = ..., file_dependencies: _Optional[_Iterable[str]] = ...) -> None: ...

class LogMessage(_message.Message):
    __slots__ = ["log_message", "severity_level", "unix_timestamp_in_ms", "entity_type", "entity_name", "runtime"]
    LOG_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_IN_MS_FIELD_NUMBER: _ClassVar[int]
    ENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_NAME_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    log_message: str
    severity_level: LogMessageSeverityLevel
    unix_timestamp_in_ms: int
    entity_type: LogMessageEntityType
    entity_name: str
    runtime: Runtime
    def __init__(self, log_message: _Optional[str] = ..., severity_level: _Optional[_Union[LogMessageSeverityLevel, str]] = ..., unix_timestamp_in_ms: _Optional[int] = ..., entity_type: _Optional[_Union[LogMessageEntityType, str]] = ..., entity_name: _Optional[str] = ..., runtime: _Optional[_Union[Runtime, str]] = ...) -> None: ...

class CLAIDConfig(_message.Message):
    __slots__ = ["hosts", "log_sink_host", "log_sink_severity_level", "log_sink_transfer_mode", "log_sink_log_storage_path", "milliseconds_deadline_to_load_modules"]
    HOSTS_FIELD_NUMBER: _ClassVar[int]
    LOG_SINK_HOST_FIELD_NUMBER: _ClassVar[int]
    LOG_SINK_SEVERITY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    LOG_SINK_TRANSFER_MODE_FIELD_NUMBER: _ClassVar[int]
    LOG_SINK_LOG_STORAGE_PATH_FIELD_NUMBER: _ClassVar[int]
    MILLISECONDS_DEADLINE_TO_LOAD_MODULES_FIELD_NUMBER: _ClassVar[int]
    hosts: _containers.RepeatedCompositeFieldContainer[HostConfig]
    log_sink_host: str
    log_sink_severity_level: LogMessageSeverityLevel
    log_sink_transfer_mode: LogSinkTransferMode
    log_sink_log_storage_path: str
    milliseconds_deadline_to_load_modules: int
    def __init__(self, hosts: _Optional[_Iterable[_Union[HostConfig, _Mapping]]] = ..., log_sink_host: _Optional[str] = ..., log_sink_severity_level: _Optional[_Union[LogMessageSeverityLevel, str]] = ..., log_sink_transfer_mode: _Optional[_Union[LogSinkTransferMode, str]] = ..., log_sink_log_storage_path: _Optional[str] = ..., milliseconds_deadline_to_load_modules: _Optional[int] = ...) -> None: ...

class HostConfig(_message.Message):
    __slots__ = ["hostname", "type", "is_server", "host_server_address", "connect_to", "modules", "log_folder", "min_log_severity_level"]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_SERVER_FIELD_NUMBER: _ClassVar[int]
    HOST_SERVER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CONNECT_TO_FIELD_NUMBER: _ClassVar[int]
    MODULES_FIELD_NUMBER: _ClassVar[int]
    LOG_FOLDER_FIELD_NUMBER: _ClassVar[int]
    MIN_LOG_SEVERITY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    hostname: str
    type: str
    is_server: bool
    host_server_address: str
    connect_to: str
    modules: _containers.RepeatedCompositeFieldContainer[ModuleConfig]
    log_folder: str
    min_log_severity_level: LogMessageSeverityLevel
    def __init__(self, hostname: _Optional[str] = ..., type: _Optional[str] = ..., is_server: bool = ..., host_server_address: _Optional[str] = ..., connect_to: _Optional[str] = ..., modules: _Optional[_Iterable[_Union[ModuleConfig, _Mapping]]] = ..., log_folder: _Optional[str] = ..., min_log_severity_level: _Optional[_Union[LogMessageSeverityLevel, str]] = ...) -> None: ...

class ModuleConfig(_message.Message):
    __slots__ = ["id", "type", "input_channels", "output_channels", "properties"]
    class InputChannelsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class OutputChannelsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INPUT_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    input_channels: _containers.ScalarMap[str, str]
    output_channels: _containers.ScalarMap[str, str]
    properties: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., input_channels: _Optional[_Mapping[str, str]] = ..., output_channels: _Optional[_Mapping[str, str]] = ..., properties: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class DataFile(_message.Message):
    __slots__ = ["relative_path", "file_data"]
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_DATA_FIELD_NUMBER: _ClassVar[int]
    relative_path: str
    file_data: bytes
    def __init__(self, relative_path: _Optional[str] = ..., file_data: _Optional[bytes] = ...) -> None: ...

class ModuleInjectionDescription(_message.Message):
    __slots__ = ["module_name", "module_file", "runtime"]
    MODULE_NAME_FIELD_NUMBER: _ClassVar[int]
    MODULE_FILE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    module_name: str
    module_file: str
    runtime: Runtime
    def __init__(self, module_name: _Optional[str] = ..., module_file: _Optional[str] = ..., runtime: _Optional[_Union[Runtime, str]] = ...) -> None: ...

class ConfigUploadPayload(_message.Message):
    __slots__ = ["config", "payload_files", "modules_to_inject", "payload_data_path"]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FILES_FIELD_NUMBER: _ClassVar[int]
    MODULES_TO_INJECT_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_DATA_PATH_FIELD_NUMBER: _ClassVar[int]
    config: CLAIDConfig
    payload_files: _containers.RepeatedCompositeFieldContainer[DataFile]
    modules_to_inject: _containers.RepeatedCompositeFieldContainer[ModuleInjectionDescription]
    payload_data_path: str
    def __init__(self, config: _Optional[_Union[CLAIDConfig, _Mapping]] = ..., payload_files: _Optional[_Iterable[_Union[DataFile, _Mapping]]] = ..., modules_to_inject: _Optional[_Iterable[_Union[ModuleInjectionDescription, _Mapping]]] = ..., payload_data_path: _Optional[str] = ...) -> None: ...

class PowerProfile(_message.Message):
    __slots__ = ["power_profile_type", "frequency", "period", "additional_information"]
    class AdditionalInformationEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    POWER_PROFILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    power_profile_type: PowerProfileType
    frequency: float
    period: float
    additional_information: _containers.ScalarMap[str, str]
    def __init__(self, power_profile_type: _Optional[_Union[PowerProfileType, str]] = ..., frequency: _Optional[float] = ..., period: _Optional[float] = ..., additional_information: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PowerSavingStrategy(_message.Message):
    __slots__ = ["battery_threshold", "active_modules", "paused_modules", "power_profiles", "wake_lock", "disable_network_connections", "disable_wifi_and_bluetooth"]
    class PowerProfilesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PowerProfile
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PowerProfile, _Mapping]] = ...) -> None: ...
    BATTERY_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_MODULES_FIELD_NUMBER: _ClassVar[int]
    PAUSED_MODULES_FIELD_NUMBER: _ClassVar[int]
    POWER_PROFILES_FIELD_NUMBER: _ClassVar[int]
    WAKE_LOCK_FIELD_NUMBER: _ClassVar[int]
    DISABLE_NETWORK_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    DISABLE_WIFI_AND_BLUETOOTH_FIELD_NUMBER: _ClassVar[int]
    battery_threshold: float
    active_modules: _containers.RepeatedScalarFieldContainer[str]
    paused_modules: _containers.RepeatedScalarFieldContainer[str]
    power_profiles: _containers.MessageMap[str, PowerProfile]
    wake_lock: bool
    disable_network_connections: bool
    disable_wifi_and_bluetooth: bool
    def __init__(self, battery_threshold: _Optional[float] = ..., active_modules: _Optional[_Iterable[str]] = ..., paused_modules: _Optional[_Iterable[str]] = ..., power_profiles: _Optional[_Mapping[str, PowerProfile]] = ..., wake_lock: bool = ..., disable_network_connections: bool = ..., disable_wifi_and_bluetooth: bool = ...) -> None: ...

class PowerSavingStrategyList(_message.Message):
    __slots__ = ["strategies"]
    STRATEGIES_FIELD_NUMBER: _ClassVar[int]
    strategies: _containers.RepeatedCompositeFieldContainer[PowerSavingStrategy]
    def __init__(self, strategies: _Optional[_Iterable[_Union[PowerSavingStrategy, _Mapping]]] = ...) -> None: ...

class CLAIDANY(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class RemoteFunctionIdentifier(_message.Message):
    __slots__ = ["function_name", "runtime", "module_id"]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    function_name: str
    runtime: Runtime
    module_id: str
    def __init__(self, function_name: _Optional[str] = ..., runtime: _Optional[_Union[Runtime, str]] = ..., module_id: _Optional[str] = ...) -> None: ...

class RemoteFunctionRequest(_message.Message):
    __slots__ = ["remote_function_identifier", "remote_future_identifier", "parameter_payloads"]
    REMOTE_FUNCTION_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FUTURE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_PAYLOADS_FIELD_NUMBER: _ClassVar[int]
    remote_function_identifier: RemoteFunctionIdentifier
    remote_future_identifier: str
    parameter_payloads: _containers.RepeatedCompositeFieldContainer[Blob]
    def __init__(self, remote_function_identifier: _Optional[_Union[RemoteFunctionIdentifier, _Mapping]] = ..., remote_future_identifier: _Optional[str] = ..., parameter_payloads: _Optional[_Iterable[_Union[Blob, _Mapping]]] = ...) -> None: ...

class RemoteFunctionReturn(_message.Message):
    __slots__ = ["execution_status", "remote_function_identifier", "remote_future_identifier"]
    EXECUTION_STATUS_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FUNCTION_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FUTURE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    execution_status: RemoteFunctionStatus
    remote_function_identifier: RemoteFunctionIdentifier
    remote_future_identifier: str
    def __init__(self, execution_status: _Optional[_Union[RemoteFunctionStatus, str]] = ..., remote_function_identifier: _Optional[_Union[RemoteFunctionIdentifier, _Mapping]] = ..., remote_future_identifier: _Optional[str] = ...) -> None: ...

class LooseDirectChannelSubscription(_message.Message):
    __slots__ = ["subscriber_runtime", "subscriber_entity", "subscribed_module", "subscribed_channel"]
    SUBSCRIBER_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBER_ENTITY_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_MODULE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    subscriber_runtime: Runtime
    subscriber_entity: str
    subscribed_module: str
    subscribed_channel: str
    def __init__(self, subscriber_runtime: _Optional[_Union[Runtime, str]] = ..., subscriber_entity: _Optional[str] = ..., subscribed_module: _Optional[str] = ..., subscribed_channel: _Optional[str] = ...) -> None: ...

class DataSyncFileDescriptor(_message.Message):
    __slots__ = ["file_size", "hash", "relative_file_path", "file_data"]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_DATA_FIELD_NUMBER: _ClassVar[int]
    file_size: int
    hash: int
    relative_file_path: str
    file_data: bytes
    def __init__(self, file_size: _Optional[int] = ..., hash: _Optional[int] = ..., relative_file_path: _Optional[str] = ..., file_data: _Optional[bytes] = ...) -> None: ...

class DataSyncFileDescriptorList(_message.Message):
    __slots__ = ["descriptors"]
    DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    descriptors: _containers.RepeatedCompositeFieldContainer[DataSyncFileDescriptor]
    def __init__(self, descriptors: _Optional[_Iterable[_Union[DataSyncFileDescriptor, _Mapping]]] = ...) -> None: ...

class DataSyncPackage(_message.Message):
    __slots__ = ["package_type", "file_descriptors"]
    PACKAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_DESCRIPTORS_FIELD_NUMBER: _ClassVar[int]
    package_type: DataSyncPackageType
    file_descriptors: DataSyncFileDescriptorList
    def __init__(self, package_type: _Optional[_Union[DataSyncPackageType, str]] = ..., file_descriptors: _Optional[_Union[DataSyncFileDescriptorList, _Mapping]] = ...) -> None: ...

class RuntimeType(_message.Message):
    __slots__ = ["runtime"]
    RUNTIME_FIELD_NUMBER: _ClassVar[int]
    runtime: Runtime
    def __init__(self, runtime: _Optional[_Union[Runtime, str]] = ...) -> None: ...

class Schedule(_message.Message):
    __slots__ = ["periodic", "timed"]
    PERIODIC_FIELD_NUMBER: _ClassVar[int]
    TIMED_FIELD_NUMBER: _ClassVar[int]
    periodic: _containers.RepeatedCompositeFieldContainer[SchedulePeriodic]
    timed: _containers.RepeatedCompositeFieldContainer[ScheduleExactTime]
    def __init__(self, periodic: _Optional[_Iterable[_Union[SchedulePeriodic, _Mapping]]] = ..., timed: _Optional[_Iterable[_Union[ScheduleExactTime, _Mapping]]] = ...) -> None: ...

class ScheduleTimeWindow(_message.Message):
    __slots__ = ["start_hour", "stop_hour"]
    START_HOUR_FIELD_NUMBER: _ClassVar[int]
    STOP_HOUR_FIELD_NUMBER: _ClassVar[int]
    start_hour: int
    stop_hour: int
    def __init__(self, start_hour: _Optional[int] = ..., stop_hour: _Optional[int] = ...) -> None: ...

class ScheduleTimeOfDay(_message.Message):
    __slots__ = ["hour", "minute", "second"]
    HOUR_FIELD_NUMBER: _ClassVar[int]
    MINUTE_FIELD_NUMBER: _ClassVar[int]
    SECOND_FIELD_NUMBER: _ClassVar[int]
    hour: int
    minute: int
    second: int
    def __init__(self, hour: _Optional[int] = ..., minute: _Optional[int] = ..., second: _Optional[int] = ...) -> None: ...

class SchedulePeriodic(_message.Message):
    __slots__ = ["first_execution_time", "only_active_between", "frequency_Hz", "frequency_kHz", "frequency_MHz", "period_milliseconds", "period_seconds", "period_minutes", "period_hours", "period_days"]
    FIRST_EXECUTION_TIME_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_BETWEEN_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_HZ_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_KHZ_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_MHZ_FIELD_NUMBER: _ClassVar[int]
    PERIOD_MILLISECONDS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_SECONDS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_MINUTES_FIELD_NUMBER: _ClassVar[int]
    PERIOD_HOURS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_DAYS_FIELD_NUMBER: _ClassVar[int]
    first_execution_time: ScheduleTimeOfDay
    only_active_between: ScheduleTimeWindow
    frequency_Hz: float
    frequency_kHz: float
    frequency_MHz: float
    period_milliseconds: float
    period_seconds: float
    period_minutes: float
    period_hours: float
    period_days: float
    def __init__(self, first_execution_time: _Optional[_Union[ScheduleTimeOfDay, _Mapping]] = ..., only_active_between: _Optional[_Union[ScheduleTimeWindow, _Mapping]] = ..., frequency_Hz: _Optional[float] = ..., frequency_kHz: _Optional[float] = ..., frequency_MHz: _Optional[float] = ..., period_milliseconds: _Optional[float] = ..., period_seconds: _Optional[float] = ..., period_minutes: _Optional[float] = ..., period_hours: _Optional[float] = ..., period_days: _Optional[float] = ...) -> None: ...

class ScheduleExactTime(_message.Message):
    __slots__ = ["time_of_day", "repeat_every_n_days"]
    TIME_OF_DAY_FIELD_NUMBER: _ClassVar[int]
    REPEAT_EVERY_N_DAYS_FIELD_NUMBER: _ClassVar[int]
    time_of_day: ScheduleTimeOfDay
    repeat_every_n_days: float
    def __init__(self, time_of_day: _Optional[_Union[ScheduleTimeOfDay, _Mapping]] = ..., repeat_every_n_days: _Optional[float] = ...) -> None: ...

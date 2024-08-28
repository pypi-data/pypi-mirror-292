from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AudioEncoding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ENCODING_PCM_8BIT: _ClassVar[AudioEncoding]
    ENCODING_PCM_16BIT: _ClassVar[AudioEncoding]
    ENCODING_PCM_FLOAT: _ClassVar[AudioEncoding]
    ENCODING_PCM_24_BIT_PACKED: _ClassVar[AudioEncoding]
    ENCODING_PCM_32_BIT: _ClassVar[AudioEncoding]

class AudioChannels(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CHANNEL_MONO: _ClassVar[AudioChannels]
    CHANNEL_STEREO: _ClassVar[AudioChannels]
    CHANNEL_QUAD: _ClassVar[AudioChannels]
    CHANNEL_5POINT1: _ClassVar[AudioChannels]
    CHANNEL_7POINT1_SURROUND: _ClassVar[AudioChannels]

class BodyLocation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    left_ankle: _ClassVar[BodyLocation]
    right_ankle: _ClassVar[BodyLocation]
    left_hip: _ClassVar[BodyLocation]
    right_hip: _ClassVar[BodyLocation]
    left_thigh: _ClassVar[BodyLocation]
    right_thigh: _ClassVar[BodyLocation]
    left_thorax: _ClassVar[BodyLocation]
    middle_left_thorax: _ClassVar[BodyLocation]
    left_upper_arm: _ClassVar[BodyLocation]
    right_upper_arm: _ClassVar[BodyLocation]
    left_wrist: _ClassVar[BodyLocation]
    right_wrist: _ClassVar[BodyLocation]

class HeartRateStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    OK: _ClassVar[HeartRateStatus]
    PAUSED_DUE_TO_OTHER_PPG_SENSOR_RUNNING: _ClassVar[HeartRateStatus]
    NO_DATA: _ClassVar[HeartRateStatus]
    PPG_SIGNAL_TOO_WEAK: _ClassVar[HeartRateStatus]
    MEASUREMENT_UNRELIABLE_DUE_TO_MOVEMENT_OR_WRONG_ATTACHMENT_PPG_WEAK: _ClassVar[HeartRateStatus]
    OFF_BODY: _ClassVar[HeartRateStatus]
    INITIALIZING: _ClassVar[HeartRateStatus]

class BatteryState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[BatteryState]
    UNPLUGGED: _ClassVar[BatteryState]
    FULL: _ClassVar[BatteryState]
    CHARGING: _ClassVar[BatteryState]
    USB_CHARGING: _ClassVar[BatteryState]
    AC_CHARGING: _ClassVar[BatteryState]
    WIRELESS_CHARGING: _ClassVar[BatteryState]

class SleepStageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    STAGE_TYPE_UNKNOWN: _ClassVar[SleepStageType]
    STAGE_TYPE_AWAKE: _ClassVar[SleepStageType]
    STAGE_TYPE_SLEEPING: _ClassVar[SleepStageType]
    STAGE_TYPE_OUT_OF_BED: _ClassVar[SleepStageType]
    STAGE_TYPE_LIGHT_SLEEP: _ClassVar[SleepStageType]
    STAGE_TYPE_DEEP_SLEEP: _ClassVar[SleepStageType]
    STAGE_TYPE_REM_SLEEP: _ClassVar[SleepStageType]
    STAGE_TYPE_AWAKE_IN_BED: _ClassVar[SleepStageType]
ENCODING_PCM_8BIT: AudioEncoding
ENCODING_PCM_16BIT: AudioEncoding
ENCODING_PCM_FLOAT: AudioEncoding
ENCODING_PCM_24_BIT_PACKED: AudioEncoding
ENCODING_PCM_32_BIT: AudioEncoding
CHANNEL_MONO: AudioChannels
CHANNEL_STEREO: AudioChannels
CHANNEL_QUAD: AudioChannels
CHANNEL_5POINT1: AudioChannels
CHANNEL_7POINT1_SURROUND: AudioChannels
left_ankle: BodyLocation
right_ankle: BodyLocation
left_hip: BodyLocation
right_hip: BodyLocation
left_thigh: BodyLocation
right_thigh: BodyLocation
left_thorax: BodyLocation
middle_left_thorax: BodyLocation
left_upper_arm: BodyLocation
right_upper_arm: BodyLocation
left_wrist: BodyLocation
right_wrist: BodyLocation
OK: HeartRateStatus
PAUSED_DUE_TO_OTHER_PPG_SENSOR_RUNNING: HeartRateStatus
NO_DATA: HeartRateStatus
PPG_SIGNAL_TOO_WEAK: HeartRateStatus
MEASUREMENT_UNRELIABLE_DUE_TO_MOVEMENT_OR_WRONG_ATTACHMENT_PPG_WEAK: HeartRateStatus
OFF_BODY: HeartRateStatus
INITIALIZING: HeartRateStatus
UNKNOWN: BatteryState
UNPLUGGED: BatteryState
FULL: BatteryState
CHARGING: BatteryState
USB_CHARGING: BatteryState
AC_CHARGING: BatteryState
WIRELESS_CHARGING: BatteryState
STAGE_TYPE_UNKNOWN: SleepStageType
STAGE_TYPE_AWAKE: SleepStageType
STAGE_TYPE_SLEEPING: SleepStageType
STAGE_TYPE_OUT_OF_BED: SleepStageType
STAGE_TYPE_LIGHT_SLEEP: SleepStageType
STAGE_TYPE_DEEP_SLEEP: SleepStageType
STAGE_TYPE_REM_SLEEP: SleepStageType
STAGE_TYPE_AWAKE_IN_BED: SleepStageType

class AudioData(_message.Message):
    __slots__ = ["data", "sampling_rate", "bit_rate", "encoding", "channels"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SAMPLING_RATE_FIELD_NUMBER: _ClassVar[int]
    BIT_RATE_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    sampling_rate: int
    bit_rate: int
    encoding: AudioEncoding
    channels: AudioChannels
    def __init__(self, data: _Optional[bytes] = ..., sampling_rate: _Optional[int] = ..., bit_rate: _Optional[int] = ..., encoding: _Optional[_Union[AudioEncoding, str]] = ..., channels: _Optional[_Union[AudioChannels, str]] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ["data", "width", "height", "channels", "data_type"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    width: int
    height: int
    channels: int
    data_type: int
    def __init__(self, data: _Optional[bytes] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., channels: _Optional[int] = ..., data_type: _Optional[int] = ...) -> None: ...

class AccelerationUnitValue(_message.Message):
    __slots__ = ["unit", "value"]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    unit: str
    value: float
    def __init__(self, unit: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class ActivityName(_message.Message):
    __slots__ = ["type"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: str
    def __init__(self, type: _Optional[str] = ...) -> None: ...

class AccelerationSample(_message.Message):
    __slots__ = ["acceleration_x", "acceleration_y", "acceleration_z", "sensor_body_location", "unix_timestamp_in_ms", "effective_time_frame"]
    ACCELERATION_X_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_Y_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_Z_FIELD_NUMBER: _ClassVar[int]
    SENSOR_BODY_LOCATION_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_IN_MS_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_TIME_FRAME_FIELD_NUMBER: _ClassVar[int]
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    sensor_body_location: str
    unix_timestamp_in_ms: int
    effective_time_frame: str
    def __init__(self, acceleration_x: _Optional[float] = ..., acceleration_y: _Optional[float] = ..., acceleration_z: _Optional[float] = ..., sensor_body_location: _Optional[str] = ..., unix_timestamp_in_ms: _Optional[int] = ..., effective_time_frame: _Optional[str] = ...) -> None: ...

class AccelerationData(_message.Message):
    __slots__ = ["samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[AccelerationSample]
    def __init__(self, samples: _Optional[_Iterable[_Union[AccelerationSample, _Mapping]]] = ...) -> None: ...

class GyroscopeSample(_message.Message):
    __slots__ = ["gyroscope_x", "gyroscope_y", "gyroscope_z", "sensor_body_location", "unix_timestamp_in_ms", "effective_time_frame"]
    GYROSCOPE_X_FIELD_NUMBER: _ClassVar[int]
    GYROSCOPE_Y_FIELD_NUMBER: _ClassVar[int]
    GYROSCOPE_Z_FIELD_NUMBER: _ClassVar[int]
    SENSOR_BODY_LOCATION_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_IN_MS_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_TIME_FRAME_FIELD_NUMBER: _ClassVar[int]
    gyroscope_x: float
    gyroscope_y: float
    gyroscope_z: float
    sensor_body_location: str
    unix_timestamp_in_ms: int
    effective_time_frame: str
    def __init__(self, gyroscope_x: _Optional[float] = ..., gyroscope_y: _Optional[float] = ..., gyroscope_z: _Optional[float] = ..., sensor_body_location: _Optional[str] = ..., unix_timestamp_in_ms: _Optional[int] = ..., effective_time_frame: _Optional[str] = ...) -> None: ...

class GyroscopeData(_message.Message):
    __slots__ = ["samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[GyroscopeSample]
    def __init__(self, samples: _Optional[_Iterable[_Union[GyroscopeSample, _Mapping]]] = ...) -> None: ...

class HeartRateSample(_message.Message):
    __slots__ = ["hr", "hrInterBeatInterval", "status", "unix_timestamp_in_ms", "effective_time_frame"]
    HR_FIELD_NUMBER: _ClassVar[int]
    HRINTERBEATINTERVAL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_IN_MS_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_TIME_FRAME_FIELD_NUMBER: _ClassVar[int]
    hr: float
    hrInterBeatInterval: int
    status: HeartRateStatus
    unix_timestamp_in_ms: int
    effective_time_frame: str
    def __init__(self, hr: _Optional[float] = ..., hrInterBeatInterval: _Optional[int] = ..., status: _Optional[_Union[HeartRateStatus, str]] = ..., unix_timestamp_in_ms: _Optional[int] = ..., effective_time_frame: _Optional[str] = ...) -> None: ...

class HeartRateData(_message.Message):
    __slots__ = ["samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[HeartRateSample]
    def __init__(self, samples: _Optional[_Iterable[_Union[HeartRateSample, _Mapping]]] = ...) -> None: ...

class BatterySample(_message.Message):
    __slots__ = ["level", "state", "unix_timestamp_in_ms"]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_IN_MS_FIELD_NUMBER: _ClassVar[int]
    level: int
    state: BatteryState
    unix_timestamp_in_ms: int
    def __init__(self, level: _Optional[int] = ..., state: _Optional[_Union[BatteryState, str]] = ..., unix_timestamp_in_ms: _Optional[int] = ...) -> None: ...

class BatteryData(_message.Message):
    __slots__ = ["samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[BatterySample]
    def __init__(self, samples: _Optional[_Iterable[_Union[BatterySample, _Mapping]]] = ...) -> None: ...

class LocationSample(_message.Message):
    __slots__ = ["provider", "floor", "timestamp", "hAccuracy", "vAccuracy", "speed", "altitude", "latitude", "longitude", "elapsedRealtimeSeconds", "bearing"]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    HACCURACY_FIELD_NUMBER: _ClassVar[int]
    VACCURACY_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ELAPSEDREALTIMESECONDS_FIELD_NUMBER: _ClassVar[int]
    BEARING_FIELD_NUMBER: _ClassVar[int]
    provider: str
    floor: int
    timestamp: int
    hAccuracy: float
    vAccuracy: float
    speed: float
    altitude: float
    latitude: float
    longitude: float
    elapsedRealtimeSeconds: float
    bearing: float
    def __init__(self, provider: _Optional[str] = ..., floor: _Optional[int] = ..., timestamp: _Optional[int] = ..., hAccuracy: _Optional[float] = ..., vAccuracy: _Optional[float] = ..., speed: _Optional[float] = ..., altitude: _Optional[float] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., elapsedRealtimeSeconds: _Optional[float] = ..., bearing: _Optional[float] = ...) -> None: ...

class LocationData(_message.Message):
    __slots__ = ["samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[LocationSample]
    def __init__(self, samples: _Optional[_Iterable[_Union[LocationSample, _Mapping]]] = ...) -> None: ...

class SleepStage(_message.Message):
    __slots__ = ["sleepStageType", "start_time_unix_timestamp", "end_time_unix_timestamp"]
    SLEEPSTAGETYPE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_UNIX_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIME_UNIX_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    sleepStageType: SleepStageType
    start_time_unix_timestamp: int
    end_time_unix_timestamp: int
    def __init__(self, sleepStageType: _Optional[_Union[SleepStageType, str]] = ..., start_time_unix_timestamp: _Optional[int] = ..., end_time_unix_timestamp: _Optional[int] = ...) -> None: ...

class SleepData(_message.Message):
    __slots__ = ["begin_of_sleep_data_interval_unix_timestamp_ms", "end_of_sleep_data_interval_unix_timestamp_ms", "stages"]
    BEGIN_OF_SLEEP_DATA_INTERVAL_UNIX_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    END_OF_SLEEP_DATA_INTERVAL_UNIX_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    STAGES_FIELD_NUMBER: _ClassVar[int]
    begin_of_sleep_data_interval_unix_timestamp_ms: int
    end_of_sleep_data_interval_unix_timestamp_ms: int
    stages: _containers.RepeatedCompositeFieldContainer[SleepStage]
    def __init__(self, begin_of_sleep_data_interval_unix_timestamp_ms: _Optional[int] = ..., end_of_sleep_data_interval_unix_timestamp_ms: _Optional[int] = ..., stages: _Optional[_Iterable[_Union[SleepStage, _Mapping]]] = ...) -> None: ...

class OxygenSaturationSample(_message.Message):
    __slots__ = ["oxygen_saturation_percentage", "unix_timestamp_ms"]
    OXYGEN_SATURATION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    oxygen_saturation_percentage: float
    unix_timestamp_ms: int
    def __init__(self, oxygen_saturation_percentage: _Optional[float] = ..., unix_timestamp_ms: _Optional[int] = ...) -> None: ...

class OxygenSaturationData(_message.Message):
    __slots__ = ["begin_of_oxygen_data_interval_unix_timestamp_ms", "end_of_oxygen_data_interval_unix_timestamp_ms", "oxygen_saturation_samples"]
    BEGIN_OF_OXYGEN_DATA_INTERVAL_UNIX_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    END_OF_OXYGEN_DATA_INTERVAL_UNIX_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    OXYGEN_SATURATION_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    begin_of_oxygen_data_interval_unix_timestamp_ms: int
    end_of_oxygen_data_interval_unix_timestamp_ms: int
    oxygen_saturation_samples: _containers.RepeatedCompositeFieldContainer[OxygenSaturationSample]
    def __init__(self, begin_of_oxygen_data_interval_unix_timestamp_ms: _Optional[int] = ..., end_of_oxygen_data_interval_unix_timestamp_ms: _Optional[int] = ..., oxygen_saturation_samples: _Optional[_Iterable[_Union[OxygenSaturationSample, _Mapping]]] = ...) -> None: ...

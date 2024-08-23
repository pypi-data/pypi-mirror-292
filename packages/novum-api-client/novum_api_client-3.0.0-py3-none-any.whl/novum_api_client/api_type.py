# pylint: disable=C0115
# flake8: noqa: E501

import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union, TypeVar, Generic
from dataclasses_json import dataclass_json, Undefined


TFields = TypeVar("TFields")


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ApiOptions(Generic[TFields]):
    query: Optional[Dict[str, str]] = field(default=None)
    filter: Optional[Any] = field(default=None)
    option: Optional[Any] = field(default=None)
    fields: Optional[Any] = field(default=None)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TProfile:
    name: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    picture: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TServiceCenterSettings:
    showAdvancedOptions: Optional[bool]
    invertAxis: Optional[bool]
    onlyShowTopLevelBatteries: Optional[bool]
    favoriteBatteriesIds: Optional[List[str]]
    batteryTableColumns: Optional[List[str]]
    dashboardTableColumns: Optional[List[str]]
    eisDatasetTableColumns: Optional[List[str]]
    capacityMeasurementTableColumns: Optional[List[str]]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserSettings:
    ServiceCenterSettings: Optional[TServiceCenterSettings]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TIDAndTimesReading:
    id: Optional[str] = None
    created_at: Optional[Union[datetime.datetime, str]] = None
    updated_at: Optional[Union[datetime.datetime, str]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TIDAndTimesEssential:
    id: str
    created_at: str
    updated_at: str


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TStats:
    last_login: Union[str, int]
    logins_count: int
    last_ip: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TMinMax:
    min: Optional[float] = None
    max: Optional[float] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TGeometricDimension:
    height: Optional[float] = None
    width: Optional[float] = None
    depth: Optional[float] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TEISSetup:
    start_frequency: Optional[float] = None
    end_frequency: Optional[float] = None
    number_of_frequencies: Optional[int] = None
    excitation_current_offset: Optional[float] = None
    excitation_current_amplitude: Optional[float] = None
    excitation_mode: Optional[int] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TChargeSetup:
    discharge_rate: Optional[float] = None
    charge_rate: Optional[float] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserDocument:
    originalFileName: Optional[str] = None
    fileName: Optional[str] = None
    fileURL: Optional[str] = None
    fileMD5: Optional[str] = None
    fileType: Optional[Dict[str, Any]] = None
    fileSize: Optional[int] = None
    aws_file_url: Optional[str] = None
    aws_file_name: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBaseDocModelReading(TIDAndTimesReading):
    creator_id: Optional[str] = None
    updater_id: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBaseDocModelEssential(TIDAndTimesEssential):
    creator_id: str
    updater_id: str


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserRole:
    """Auth0 roles"""

    UserRole: str = "user"
    AdminRole: str = "admin"
    NovumExpertRole: str = "novumExpert"
    SupportRole: str = "support"
    CleanerRole: str = "cleaner"
    InvoiceCreatorRole: str = "invoiceCreator"
    ProductManagerRole: str = "productManager"
    SuperReaderRole: str = "superReader"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserOptional:
    stats: Optional[TStats] = None
    meta_data: Optional[dict] = None
    scope: Optional[str] = None
    expires_at: Optional[str] = None
    refresh_token: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserReadingOptional:
    jwt: Optional[str] = None
    auth0_id: Optional[str] = None
    roles: Optional[List[TUserRole]] = None
    profile: Optional[TProfile] = None
    settings: Optional[TUserSettings] = None
    permissions: Optional[List[str]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserReading(TUserReadingOptional, TUserOptional, TIDAndTimesReading):
    """ "test"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserWritingRequired:
    "TUser"
    jwt: str
    auth0_id: str
    roles: List[TUserRole]
    profile: TProfile
    settings: TUserSettings
    permissions: List[str]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserWriting(TUserOptional, TIDAndTimesReading, TUserWritingRequired):
    """test"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUserRequired(TUserWriting, TIDAndTimesReading):
    """TUserRequired"""

    @classmethod
    def from_reading(cls, reading: TUserReading) -> "TUserRequired":
        """from reading to required type"""
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TUserWritingRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_user(cls, typed_class: "TUser") -> "TUserRequired":
        """from user to required type"""
        typed_class_dict = asdict(typed_class)
        reading_fields = {
            k: v for k, v in typed_class_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TUser(TIDAndTimesEssential, TUserRequired):
    """TUser"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDetails:
    statusCode: Optional[int]
    headers: Optional[Dict[str, str]]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAPIErrorReading:
    error: Optional[str] = None
    details: Optional[TDetails] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAPIErrorEssential:
    error: Optional[str]
    details: Optional[TDetails]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TVersionOptional:
    hash: Optional[str] = None
    branch: Optional[str] = None
    build_date: Optional[Union[str, datetime.datetime]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TVersionReadingOptional:
    tag: Optional[str] = None
    name: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TVersionReading(TVersionReadingOptional, TVersionOptional, TAPIErrorReading):
    """TVersion"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TVersionWritingRequired:
    "TVersion"
    tag: str
    name: str


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TVersionWriting(TVersionOptional, TAPIErrorReading, TVersionWritingRequired):
    """TVersion"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TVersionRequired(TVersionWriting, TAPIErrorReading):
    """TVersionRequired"""

    @classmethod
    def from_reading(cls, reading: TVersionReading) -> "TVersionRequired":
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TVersionWritingRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_version(cls, typed_class: "TVersion") -> "TVersionRequired":
        """from version to required type"""
        typed_class_dict = asdict(typed_class)
        reading_fields = {
            k: v for k, v in typed_class_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TVersion(TVersionRequired, TAPIErrorReading):
    """TVersion"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAPIInfoWriting:
    name: Optional[str] = None
    dbName: Optional[str] = None
    version: Optional[TVersion] = None
    description: Optional[str] = None
    dev_container_mode: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAPIInfoRequired(TAPIInfoWriting, TAPIErrorReading):
    "Info"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAPIInfo(TAPIErrorEssential, TAPIInfoRequired):
    "Info"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TLatLng:
    planet: str
    lat: float
    lng: float


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAddress:
    country: str
    country_code: str
    city: str
    state: str
    postal_code: str
    street: str
    street_number: str


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TLocation:
    geo: TLatLng
    address: TAddress


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TMetrics:
    measured_at: Union[str, datetime.datetime]
    state_of_health: float
    state_of_charge: float
    temperature: float


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TIndicatorProperty:
    scale: float
    top: float
    left: float


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TIndicatorProperties:
    indicator_properties: Dict[str, TIndicatorProperty]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TInsights:
    enabled: Optional[bool] = None
    image: Optional[str] = None
    image_styles: Optional[str] = None
    indicator_properties: Optional[TIndicatorProperties] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAtomicState:
    updated_at: Union[datetime.datetime, str]
    value: float
    origin_id: Optional[str]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryState:
    state_of_health: Optional[TAtomicState] = None
    state_of_charge: Optional[TAtomicState] = None
    current: Optional[TAtomicState] = None
    voltage: Optional[TAtomicState] = None
    temperature: Optional[TAtomicState] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TTreeProperties:
    is_leaf: Optional[bool] = None
    enabled: Optional[bool] = None
    parent: Optional[str] = None
    ancestors: Optional[List[str]] = None
    children_topology: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TEstimatorOverview:
    file_name: Optional[str]
    description: Optional[str]
    time: Optional[Union[str, datetime.datetime]]
    last_valid_time: Optional[Union[str, datetime.datetime]]
    model_state: Optional[List[float]]
    last_valid_model_state: Optional[List[float]]
    report: Optional[str]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TEstimators:
    soc_estimator: Optional[TEstimatorOverview]


TBatteryGrade = Literal[
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "?",
]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TLowerSoHLimit:
    soh: float
    grade: TBatteryGrade


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryTypeOptional:
    description: Optional[str] = None
    cell_chemistry: Optional[str] = None
    battery_design: Optional[str] = None
    hierarchy_level: Optional[str] = None
    allowed_voltage_range_single_cell: Optional[TMinMax] = None
    allowed_voltage_range_battery_pack: Optional[TMinMax] = None
    allowed_peak_charge_current_range: Optional[TMinMax] = None
    allowed_peak_discharge_current_range: Optional[TMinMax] = None
    allowed_continuous_charge_current_range: Optional[TMinMax] = None
    allowed_temperature_range_for_charging: Optional[TMinMax] = None
    allowed_temperature_range_for_storage: Optional[TMinMax] = None
    allowed_temperature_range_for_use: Optional[TMinMax] = None
    internal_resistance: Optional[float] = None
    self_discharge_rate_per_month: Optional[float] = None
    allowed_cycles_for_100_depth_of_discharge: Optional[int] = None
    mass_based_power_density: Optional[float] = None
    cell_mass: Optional[float] = None
    outer_geometric_dimension: Optional[TGeometricDimension] = None
    default_eis_setup: Optional[TEISSetup] = None
    default_charge_setup: Optional[TChargeSetup] = None
    image: Optional[str] = None
    user_docs: Optional[List[TUserDocument]] = None
    user_doc_ids: Optional[List[str]] = None
    public: Optional[bool] = None
    tags: Optional[List[str]] = None
    grade_lookup_table: Optional[List[TLowerSoHLimit]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryTypeReadingOptional:
    """Reading TBattery Type"""

    name: Optional[str] = None
    manufacturer: Optional[str] = None
    nominal_voltage: Optional[float] = None
    nominal_capacity: Optional[float] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryTypeReading(
    TBatteryTypeReadingOptional, TBatteryTypeOptional, TBaseDocModelReading
):
    """Reading TBattery Type"""

    @classmethod
    def from_battery_type(cls, battery_type: "TBatteryType") -> "TBatteryTypeReading":
        battery_type_dict = asdict(battery_type)
        reading_fields = {
            k: v for k, v in battery_type_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryTypeWritingRequired:
    """Writing TBattery"""

    name: str
    manufacturer: str
    nominal_voltage: float
    nominal_capacity: float


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryTypeWriting(
    TBatteryTypeOptional, TBaseDocModelReading, TBatteryTypeWritingRequired
):
    """TBatteryType"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryTypeRequired(TBatteryTypeWriting, TBaseDocModelReading):
    """TBatteryType"""

    @classmethod
    def from_dict(cls, data: dict) -> "TBatteryTypeRequired":
        """from dict to required type"""
        required_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**required_fields)

    @classmethod
    def from_reading(cls, reading: TBatteryTypeReading) -> "TBatteryTypeRequired":
        """from reading to required type"""
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TBatteryTypeWritingRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_battery_type(cls, battery_type: "TBatteryType") -> "TBatteryTypeRequired":
        """from dict to type to required"""
        return cls.from_dict(asdict(battery_type))


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryType(TBaseDocModelEssential, TBatteryTypeRequired):
    """TBatteryType"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryOptional:
    serial_number: Optional[str] = None
    description: Optional[str] = None
    location: Optional[TLocation] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = None
    metrics: Optional[TMetrics] = None
    insights: Optional[TInsights] = None
    state: Optional[TBatteryState] = None
    tree: Optional[TTreeProperties] = None
    estimators: Optional[TEstimators] = None
    user_doc_ids: Optional[List[str]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryReadingOptional:
    name: Optional[str] = None
    battery_type: Optional[TBatteryTypeRequired] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryReading(TBatteryReadingOptional, TBatteryOptional, TBaseDocModelReading):
    """TBattery"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryWritingRequired:
    "TBattery with required fields"
    name: str
    battery_type: TBatteryTypeRequired


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryWriting(TBatteryOptional, TBaseDocModelReading, TBatteryWritingRequired):
    """TBattery"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBatteryRequired(TBatteryWriting, TBaseDocModelReading):
    """TBatteryRequired"""

    @classmethod
    def from_reading(cls, reading: TBatteryReading) -> "TBatteryRequired":
        """from reading to required type"""
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TBatteryWritingRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_battery(cls, typed_class: "TBattery") -> "TBatteryRequired":
        typed_class_dict = asdict(typed_class)
        reading_fields = {
            k: v for k, v in typed_class_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TBattery(TBaseDocModelEssential, TBatteryRequired):
    """TBattery"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TChargeTypes:
    UNKNOWN = "UNKNOWN"
    CC = "CC"
    CCCV = "CCCV"
    CCPulse = "CCPulse"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TChargeCycle:
    timestamp: Optional[Union[str, datetime.datetime]]
    voltage: Optional[float]  # in Voltage (V)
    current: Optional[float]  # in Ampere (A)
    charge: Optional[float]  # in AmpereHours (Ah)
    temperature: Optional[float] = None  # in °C (K)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TCapacityMeasurementOptional:
    context_id: Optional[str] = None
    battery: Optional[TBatteryRequired] = None
    end_time: Optional[Union[str, datetime.datetime]] = None
    current_setpoint: Optional[float] = None  # in Ampere (A)
    voltage_setpoint: Optional[float] = None  # in Voltage (V)
    ambient_temperature: Optional[float] = None  # in °C (K)
    device_name: Optional[str] = None
    device_info: Optional[str] = None
    voltage_min: Optional[float] = None  # in Voltage (V)
    voltage_max: Optional[float] = None  # in Voltage (V)
    capacity: Optional[float] = None  # in AmpereHours (Ah)
    state_of_health: Optional[float] = None
    internal_resistance: Optional[float] = None  # in Ohm (Ω)
    grade: Optional[str] = None
    is_preview: Optional[bool] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TCapacityMeasurementReadingOptional:
    tags: Optional[List[str]] = None
    charge_cycles: Optional[List[TChargeCycle]] = None
    start_time: Optional[Union[str, datetime.datetime]] = None
    charge_type: Optional[TChargeTypes] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TCapacityMeasurementReading(
    TCapacityMeasurementReadingOptional,
    TCapacityMeasurementOptional,
    TBaseDocModelReading,
):
    """TCapa"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TCapacityMeasurementWritingRequired:
    """TCapacityMeasurement"""

    tags: List[str]
    charge_cycles: List[TChargeCycle]
    start_time: Union[str, datetime.datetime]
    charge_type: TChargeTypes


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TCapacityMeasurementWriting(
    TCapacityMeasurementOptional,
    TBaseDocModelReading,
    TCapacityMeasurementWritingRequired,
):
    """TCapacityMeasurements"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TCapacityMeasurementRequired(TCapacityMeasurementWriting, TBaseDocModelReading):
    """TCapacityMeasurementsRequired"""

    @classmethod
    def from_reading(
        cls, reading: TCapacityMeasurementReading
    ) -> "TCapacityMeasurementRequired":
        """from reading to required type"""
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TCapacityMeasurementWritingRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_capacity_measurement(
        cls, typed_class: "TCapacityMeasurement"
    ) -> "TCapacityMeasurementRequired":
        typed_class_dict = asdict(typed_class)
        reading_fields = {
            k: v for k, v in typed_class_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TCapacityMeasurement(TBaseDocModelEssential, TCapacityMeasurementRequired):
    """TCapacityMeasurements"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TTimedMeasure:
    before: Optional[float]
    after: Optional[float]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TMeasurementCycle:
    frequency: float  # frequency of the periodic excitation in Hz
    amplitude: float  # amplitude of the oscillation current in A
    phase_shift: float  # phase shift of the oscillation current
    temperature: Optional[float]
    voltage: Optional[float]  # voltage measured before the excitation in V
    time_delta: Optional[float]  # in seconds
    quality: Optional[float]  # a quality indicator
    voltage_raw_values: Optional[List[float]]
    current_raw_values: Optional[List[float]]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TRemoteProcedureReport:
    success: bool
    report: str


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceSpecs:
    max_voltage: Optional[int] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMetaOptional:

    description: Optional[str] = None
    last_connected_at: Optional[Union[str, datetime.datetime]] = None
    firmware: Optional[TVersionRequired] = None
    specs: Optional[TDeviceSpecs] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMetaReadingOptional:
    name: Optional[str] = None
    cpu_id: Optional[str] = None
    serial: Optional[str] = None
    product_id: Optional[str] = None
    revision: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMetaReading(
    TDeviceMetaReadingOptional, TDeviceMetaOptional, TBaseDocModelReading
):
    """TDeviceRequired"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMetaWriteRequired:
    name: str
    cpu_id: str
    serial: str
    product_id: str
    revision: str


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMetaWriting(
    TDeviceMetaOptional, TBaseDocModelReading, TDeviceMetaWriteRequired
):
    """TDeviceRequired"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMetaRequired(TDeviceMetaWriting, TBaseDocModelReading):
    """TDeviceRequired"""

    @classmethod
    def from_reading(cls, reading: TDeviceMetaReading) -> "TDeviceMetaRequired":
        """from reading to required type"""
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TDeviceMetaRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_device_meta(cls, typed_class: "TDeviceMeta") -> "TDeviceMetaRequired":
        typed_class_dict = asdict(typed_class)
        reading_fields = {
            k: v for k, v in typed_class_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMeta(TBaseDocModelEssential, TDeviceMetaRequired):
    """TDevice"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TProductReading(TBaseDocModelReading):
    gtin: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TProduct(TBaseDocModelEssential):
    gtin: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TMeasured:
    start_time: Optional[Union[datetime.datetime, str]] = None
    end_time: Optional[Union[datetime.datetime, str]] = None
    eis_setup: Optional[TEISSetup] = None
    voltage: Optional[TTimedMeasure] = None
    ambient_temperature: Optional[TTimedMeasure] = None
    battery_temperature: Optional[TTimedMeasure] = None
    measurement_cycles: Optional[List[TMeasurementCycle]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TAnalysis:
    grade: Optional[str] = None
    state_of_health: Optional[float] = None
    state_of_charge: Optional[float] = None
    temperature: Optional[float] = None
    enforce_capacity_test: Optional[bool] = None
    reports: Optional[Dict[str, TRemoteProcedureReport]] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDatasetMeta:
    device: TDeviceMetaRequired
    tags: List[str]
    client_software: TVersionRequired
    comment: Optional[str] = None
    battery: Optional[TBatteryRequired] = None
    user_defined: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDatasetOptional:
    show_in_chart: Optional[bool] = None
    context_id: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDatasetReadingOptional:
    measured: Optional[TMeasured] = None
    analysis: Optional[TAnalysis] = None
    meta: Optional[TDatasetMeta] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDatasetReading(TDatasetReadingOptional, TDatasetOptional, TBaseDocModelReading):
    """TDataset"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDatasetWritingRequired:
    """TDataset"""

    measured: TMeasured
    analysis: TAnalysis
    meta: TDatasetMeta


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDatasetWriting(TDatasetOptional, TBaseDocModelReading, TDatasetWritingRequired):
    """TDataset"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDatasetRequired(TDatasetWriting, TBaseDocModelReading):
    """TDatasetRequired"""

    @classmethod
    def from_reading(cls, reading: TDatasetReading) -> "TDatasetRequired":
        """from reading to required type"""
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TBatteryTypeWritingRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_data_set(cls, typed_class: "TDataset") -> "TDatasetRequired":
        typed_class_dict = asdict(typed_class)
        reading_fields = {
            k: v for k, v in typed_class_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDataset(TBaseDocModelEssential, TDatasetRequired):
    """TDataset"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class UITMeasurement:
    time: str
    voltage: Optional[float]
    current: Optional[float]
    temperature: Optional[float]
    charge: Optional[float]
    soc: Optional[float]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TDeviceMeasurement:
    device_id: str
    measurements: List[UITMeasurement]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReadDeviceMeasurementsResult:
    results: List[UITMeasurement]
    rejectedDeviceIds: List[str]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TWriteDeviceMeasurementsResult:
    handledDevices: List[str]
    rejectedDevices: List[str]
    handledMeasurements: int
    rejectedMeasurements: int


TMeasurand = Literal[
    "time", "voltage", "current", "temperature", "charge", "soc", "meta"
]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReadDeviceMeasurementsFilter:
    device_ids: List[str]
    measurands: List[TMeasurand]
    start: str
    end: str
    selection: Optional[str] = None
    count: Optional[int] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ReportStates:
    Unread = "unread"
    Viewed = "viewed"
    Acknowledged = "acknowledged"


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReportOptional:
    meta: Optional[dict] = None
    user_doc_ids: Optional[List[str]] = None
    origin_id: Optional[str] = None
    state: Optional[ReportStates] = None
    context_id: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReportReadingOptional:
    title: Optional[str] = None
    description: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReportReading(TReportReadingOptional, TReportOptional, TBaseDocModelReading):
    """TReport"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReportWritingRequired:
    """TReportWritingRequired"""

    title: Optional[str]
    description: Optional[str]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReportWriting(TReportOptional, TBaseDocModelReading, TReportWritingRequired):
    """TReportWriting"""


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReportRequired(TReportWriting, TBaseDocModelReading):
    """TReport"""

    @classmethod
    def from_reading(cls, reading: TReportReading) -> "TReportRequired":
        """from reading to required type"""
        reading_dict = asdict(reading)
        required_fields = {
            k: v
            for k, v in reading_dict.items()
            if k in TReportWritingRequired.__annotations__
        }
        return cls(**required_fields)

    @classmethod
    def from_report(cls, typed_class: "TReport") -> "TReportRequired":
        typed_class_dict = asdict(typed_class)
        reading_fields = {
            k: v for k, v in typed_class_dict.items() if k in cls.__annotations__
        }
        return cls(**reading_fields)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TReport(TBaseDocModelEssential, TReportRequired):
    """TReport"""

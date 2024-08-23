# flake8: noqa: E501

import json
from dataclasses import dataclass
from threading import Timer
from typing import Optional, List
import warnings
import requests
from .base_client import (
    PRODUCTION_API_HOST,
    TOKEN_REFRESH_INTERVAL_SCALE,
    BaseAPIClient,
    NovumAPIError,
)
from .api_type import (
    TUser,
    TReport,
    TBattery,
    TVersion,
    TDataset,
    ApiOptions,
    TBatteryType,
    TUserDocument,
    TReportReading,
    TBatteryReading,
    TDatasetReading,
    TReportRequired,
    TAPIInfoRequired,
    TDatasetRequired,
    TBatteryRequired,
    TDeviceMeasurement,
    TBatteryTypeReading,
    TCapacityMeasurement,
    TBatteryTypeRequired,
    TCapacityMeasurementReading,
    TCapacityMeasurementRequired,
    TReadDeviceMeasurementsResult,
    TReadDeviceMeasurementsFilter,
    TWriteDeviceMeasurementsResult,
)


@dataclass
class NovumAPIClient(BaseAPIClient):
    """NovumAPIClient class"""

    def __init__(
        self,
        host: str = PRODUCTION_API_HOST,
        user: Optional[TUser] = None,
        check_ssl_certification: Optional[bool] = True,
        refresh_token_warning: Optional[bool] = True,
        refresh_interval_scale: float = TOKEN_REFRESH_INTERVAL_SCALE,
        _relogin_timer_handle: Optional[Timer] = None,
        _authenticated: Optional[bool] = False,
    ):
        super().__init__(
            user=user if user is not None else self.user,
            host=host if host is not None else self.host,
            check_ssl_certification=check_ssl_certification
            if check_ssl_certification is not None
            else self.check_ssl_certification,
            refresh_token_warning=refresh_token_warning
            if refresh_token_warning is not None
            else self.refresh_token_warning,
            refresh_interval_scale=refresh_interval_scale
            if refresh_interval_scale is not None
            else self.refresh_interval_scale,
            _relogin_timer_handle=_relogin_timer_handle
            if _relogin_timer_handle is not None
            else self._relogin_timer_handle,
            _authenticated=_authenticated
            if _authenticated is not None
            else self._authenticated,
        )

    # ********************************************************
    # Section for the Service Center info
    # ********************************************************

    def ping(self) -> dict:
        """Ping API."""
        return self._get_json("/api/batman/v1/")

    def get_info(self) -> TAPIInfoRequired:
        """Get info."""
        info = self._get_json("/api/batman/v1/info")
        return TAPIInfoRequired(**info)

    def get_version(self) -> TVersion:
        """Check version."""
        version = self._get_json("/api/batman/v1/version")
        return TVersion(**version)

    # ********************************************************
    # Section for the users
    # ********************************************************

    def login(
        self, email: str, password: str, store_user=True, timeout: float = 4
    ) -> Optional[TUser]:
        """Login."""
        header = {"authorization": "auth", "content-type": "application/json"}
        payload = {"username": email, "password": password}
        response = requests.post(
            self.host + "/api/batman/v1/login",
            data=json.dumps(payload),
            headers=header,
            timeout=timeout,
            verify=self.check_ssl_certification,
        )
        if response.status_code == requests.codes.get("ok"):
            if store_user is True:
                user = response.json()
                self.user = TUser(**user)
                self._install_token_refresh_procedure()
                self.headers = dict(
                    {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + str(self.user.jwt),
                    }
                )

            return self.user

        raise NovumAPIError(response.text, response.status_code)

    def logout(self):
        """Log out."""
        return self._get_json("/api/batman/v1/logout")

    def check_current_user_still_authenticated(self) -> dict:
        """Check authentication."""

        return self._get_json("/api/batman/v1/check_token")

    # ********************************************************
    # Section for the Battery Types
    # ********************************************************

    def get_battery_types(
        self,
        api_options: Optional[ApiOptions[TBatteryTypeReading]] = None,
        timeout: float = 4.0,
    ) -> List[TBatteryTypeReading]:
        """Get battery types."""
        battery_types_list = self._get_json(
            "/api/batman/v1/batteryTypes",
            api_options=api_options,
            timeout=timeout,
        )

        battery_types = [
            TBatteryTypeReading(**battery_type) for battery_type in battery_types_list
        ]

        return battery_types

    def get_battery_types_count(
        self,
        api_options: Optional[ApiOptions[TBatteryTypeReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of battery types."""
        return self._get_json(
            "/api/batman/v1/batteryTypes/count",
            api_options=api_options,
            timeout=timeout,
        )  # type: ignore

    def get_battery_types_by_id(
        self, battery_type_id: str, timeout: float = 4.0
    ) -> TBatteryTypeReading:
        """Get battery type by id."""
        battery_type = self._get_json(
            f"/api/batman/v1/batteryTypes/{battery_type_id}", timeout=timeout
        )
        return TBatteryTypeReading(**battery_type)

    def remove_battery_types_by_id(
        self, battery_type_id: str, timeout: float = 4.0
    ) -> None:
        """Delete battery type by id."""
        self._delete_json(
            f"/api/batman/v1/batteryTypes/{battery_type_id}", timeout=timeout
        )

    def create_battery_type(
        self,
        battery_type: TBatteryTypeRequired,
        timeout: float = 4.0,
    ) -> TBatteryType:
        """Create battery type."""
        created_battery_type = self._post_json(
            "/api/batman/v1/batteryTypes", input_data=battery_type, timeout=timeout
        )
        return TBatteryType(**created_battery_type)

    def update_battery_type_by_id(
        self,
        battery_type_id: str,
        battery_type_update: TBatteryTypeReading,
        timeout: float = 4.0,
    ) -> TBatteryTypeReading:
        """Update battery type by id."""
        updated_battery_type = self._put_json(
            f"/api/batman/v1/batteryTypes/{battery_type_id}",
            input_data=battery_type_update,
            timeout=timeout,
        )
        return TBatteryTypeReading(**updated_battery_type)

    # ********************************************************
    # Section for the Datasets
    # ********************************************************

    def dataset_exists_on_remote(self, dataset_id: str, timeout: float = 4.0) -> bool:
        """Check remote data."""
        response = self._get_json(
            f"/api/batman/v1/datasets/{dataset_id}", timeout=timeout
        )
        try:
            if len(response["measured"]["measurement_cycles"]) != 0:
                return True
            return False
        except KeyError:
            return False

    def create_dataset(
        self, dataset: TDatasetRequired, timeout: float = 4.0
    ) -> TDataset:
        """Create EIS measurement."""
        created_dataset = self._post_json(
            "/api/batman/v1/datasets", input_data=dataset, timeout=timeout
        )
        return TDataset(**created_dataset)

    def get_dataset_by_id(self, dataset_id: str, timeout: float = 4.0) -> TDataset:
        """Get EIS measurement by id."""
        dataset = self._get_json(
            f"/api/batman/v1/datasets/{dataset_id}", timeout=timeout
        )
        return TDataset(**dataset)

    def get_datasets(
        self,
        api_options: Optional[ApiOptions[TDatasetReading]] = None,
        timeout: float = 4.0,
    ) -> List[TDatasetReading]:
        """Get EIS measurements."""
        dataset_list = self._get_json(
            "/api/batman/v1/datasets",
            api_options=api_options,
            timeout=timeout,
        )
        datasets = [TDatasetReading(**dataset) for dataset in dataset_list]

        return datasets

    def get_datasets_count(
        self,
        api_options: Optional[ApiOptions[TDatasetReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of EIS measurements."""
        return self._get_json(
            "/api/batman/v1/datasets/count",
            api_options=api_options,
            timeout=timeout,
        )  # type: ignore

    def get_datasets_count_by_battery(
        self,
        battery: TBatteryReading,
        api_options: Optional[ApiOptions[TDatasetReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of EIS measurements by battery."""
        filter_with_id = {"meta.battery._id": battery.id}
        if api_options is None:
            api_options = ApiOptions[TDatasetReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id

        response = self._get_json(
            "/api/batman/v1/datasets/count",
            api_options=api_options,
            timeout=timeout,
        )
        return response  # type: ignore

    def update_dataset_by_id(
        self, dataset_id: str, dataset: TDatasetRequired, timeout: float = 4.0
    ) -> TDatasetReading:
        """Update EIS measurement by id."""
        updated_dataset = self._put_json(
            f"/api/batman/v1/datasets/{dataset_id}",
            input_data=dataset,
            timeout=timeout,
        )
        return TDatasetReading(**updated_dataset)

    def remove_dataset_by_id(self, dataset_id: str, timeout: float = 4.0) -> None:
        """Delete EIS measurement by id."""
        self._delete_json(f"/api/batman/v1/datasets/{dataset_id}", timeout=timeout)

    # ********************************************************
    # Section for the Battery
    # ********************************************************

    def create_battery(
        self, battery: TBatteryRequired, timeout: float = 4.0
    ) -> TBattery:
        """Create a battery."""
        created_battery = self._post_json(
            "/api/batman/v1/batteries", input_data=battery, timeout=timeout
        )
        return TBattery(**created_battery)

    def get_battery_by_id(
        self, battery_id: str, timeout: float = 4.0
    ) -> TBatteryReading:
        """Get battery by id."""
        battery = self._get_json(
            f"/api/batman/v1/batteries/{battery_id}", timeout=timeout
        )

        return TBatteryReading(**battery)

    def update_battery(
        self, battery: TBatteryReading, timeout: float = 4.0
    ) -> TBatteryReading:
        """Update a battery."""
        updated_battery = self._put_json(
            f"/api/batman/v1/batteries/{battery.id}",
            input_data=battery,
            timeout=timeout,
        )

        return TBatteryReading(**updated_battery)

    def update_battery_by_id(
        self, battery_id: str, battery_update: TBatteryReading, timeout: float = 4.0
    ) -> TBatteryReading:
        """Update a battery by id."""
        updated_battery = self._put_json(
            f"/api/batman/v1/batteries/{battery_id}",
            input_data=battery_update,
            timeout=timeout,
        )
        return TBatteryReading(**updated_battery)

    def remove_battery_by_id(self, battery_id: str, timeout: float = 4.0) -> None:
        """Delete a battery by id."""
        self._delete_json(f"/api/batman/v1/batteries/{battery_id}", timeout=timeout)

    def get_batteries(
        self,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> List[TBatteryReading]:
        """Get batteries."""
        battery_list = self._get_json(
            "/api/batman/v1/batteries",
            api_options=api_options,
            timeout=timeout,
        )
        batteries = [TBatteryReading(**battery) for battery in battery_list]

        return batteries

    def get_batteries_count(
        self,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of batteries."""
        return self._get_json(
            "/api/batman/v1/batteries/count",
            api_options=api_options,
            timeout=timeout,
        )  # type: ignore

    def get_children_of_battery_by_id(
        self,
        parent_battery_id: str,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> List[TBatteryReading]:
        """Get children of a battery using the id."""
        filter_with_id = {"tree.parent": parent_battery_id}

        if api_options is None:
            api_options = ApiOptions[TBatteryReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id

        battery_list = self._get_json(
            "/api/batman/v1/batteries",
            api_options=api_options,
            timeout=timeout,
        )
        batteries = [TBatteryReading(**battery) for battery in battery_list]

        return batteries

    def get_children_of_battery_by_id_count(
        self,
        parent_battery_id: str,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of children by battery id."""
        filter_with_id = {"tree.parent": parent_battery_id}
        if api_options is None:
            api_options = ApiOptions[TBatteryReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id

        response = self._get_json(
            "/api/batman/v1/batteries/count",
            api_options=api_options,
            timeout=timeout,
        )
        return response  # type: ignore

    def get_leaves_of_battery_by_id(
        self,
        ancestor_battery_id: str,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> List[TBatteryReading]:
        """Get all leaves of a tree of battery."""
        filter_with_id = {"tree.is_leaf": True, "tree.ancestors": ancestor_battery_id}
        if api_options is None:
            api_options = ApiOptions[TBatteryReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id

        battery_list = self._get_json(
            "/api/batman/v1/batteries",
            api_options=api_options,
            timeout=timeout,
        )
        batteries = [TBatteryReading(**battery) for battery in battery_list]
        return batteries

    def get_leaves_of_battery_by_id_count(
        self,
        ancestor_battery_id: str,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> List[TBatteryReading]:
        """Get amount of leaves of a level top(accordingly on a tree) battery."""
        filter_with_id = {"tree.is_leaf": True, "tree.ancestors": ancestor_battery_id}

        if api_options is None:
            api_options = ApiOptions[TBatteryReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id

        battery_list = self._get_json(
            "/api/batman/v1/batteries/count",
            api_options=api_options,
            timeout=timeout,
        )
        batteries = [TBatteryReading(**battery) for battery in battery_list]
        return batteries

    def get_descendants_of_battery_by_id(
        self,
        ancestor_battery_id: str,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> List[TBatteryReading]:
        """Get all descendants on the tree by battery id."""
        filter_with_id = {"tree.ancestors": ancestor_battery_id}
        if api_options is None:
            api_options = ApiOptions[TBatteryReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id
        battery_list = self._get_json(
            "/api/batman/v1/batteries",
            api_options=api_options,
            timeout=timeout,
        )
        batteries = [TBatteryReading(**battery) for battery in battery_list]
        return batteries

    def get_descendants_of_battery_by_id_count(
        self,
        ancestor_battery_id: str,
        api_options: Optional[ApiOptions[TBatteryReading]] = None,
        timeout: float = 4.0,
    ) -> List[TBatteryReading]:
        """Get amount of descendants on the tree by battery id."""
        filter_with_id = {"tree.ancestors": ancestor_battery_id}
        if api_options is None:
            api_options = ApiOptions[TBatteryReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id

        battery_list = self._get_json(
            "/api/batman/v1/batteries/count",
            api_options=api_options,
            timeout=timeout,
        )
        batteries = [TBatteryReading(**battery) for battery in battery_list]
        return batteries

    # ********************************************************
    # Section for the CapacityMeasurement
    # ********************************************************

    def create_capacity_measurement(
        self, capacity_measurement: TCapacityMeasurementRequired, timeout: float = 4.0
    ) -> TCapacityMeasurement:
        """Create a capacity measurement."""
        response = self._post_json(
            "/api/batman/v1/capacityMeasurements",
            input_data=capacity_measurement,
            timeout=timeout,
        )

        return TCapacityMeasurement(**response)

    def update_capacity_measurement_by_id(
        self,
        capacity_measurement_id: str,
        capacity_measurement: TCapacityMeasurementRequired,
        timeout: float = 4.0,
    ) -> TCapacityMeasurementReading:
        """Update a capacity measurement by id."""
        updated_capacity_measurement = self._put_json(
            f"/api/batman/v1/capacityMeasurements/{capacity_measurement_id}",
            input_data=capacity_measurement,
            timeout=timeout,
        )
        return TCapacityMeasurementReading(**updated_capacity_measurement)

    def remove_capacity_measurement_by_id(
        self, capacity_measurement_id: str, timeout: float = 4.0
    ) -> None:
        """Delete capacity measurement by id."""
        self._delete_json(
            f"/api/batman/v1/capacityMeasurements/{capacity_measurement_id}",
            timeout=timeout,
        )

    def get_capacity_measurement(
        self,
        api_options: Optional[ApiOptions[TCapacityMeasurementReading]] = None,
        timeout: float = 4.0,
    ) -> List[TCapacityMeasurementReading]:
        """Get capacity measurements (deprecated)."""
        warnings.warn(
            "Function get_capacity_measurement is deprecated, use get_capacity_measurements instead.",
            DeprecationWarning,
        )

        capacity_measurements = self.get_capacity_measurements(
            api_options=api_options,
            timeout=timeout,
        )

        return capacity_measurements

    def get_capacity_measurements(
        self,
        api_options: Optional[ApiOptions[TCapacityMeasurementReading]] = None,
        timeout: float = 4.0,
    ) -> List[TCapacityMeasurementReading]:
        """Get capacity measurements."""
        capacity_measurement_list = self._get_json(
            "/api/batman/v1/capacityMeasurements",
            api_options=api_options,
            timeout=timeout,
        )

        capacity_measurements = [
            TCapacityMeasurementReading(**capa) for capa in capacity_measurement_list
        ]

        return capacity_measurements

    def get_capacity_measurement_count(
        self,
        api_options: Optional[ApiOptions[TCapacityMeasurementReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of capacity measurements (deprecated)."""
        warnings.warn(
            "Function get_capacity_measurement_count is deprecated, use get_capacity_measurements_count instead.",
            DeprecationWarning,
        )
        capacity_measurements_count = self.get_capacity_measurement_count(
            api_options=api_options,
            timeout=timeout,
        )

        return capacity_measurements_count

    def get_capacity_measurements_count(
        self,
        api_options: Optional[ApiOptions[TCapacityMeasurementReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of capacity measurements."""
        response = self._get_json(
            "/api/batman/v1/capacityMeasurements/count",
            api_options=api_options,
            timeout=timeout,
        )
        return response  # type: ignore

    def get_capacity_measurement_by_id(
        self, capacity_measurement_id: str, timeout: float = 4.0
    ) -> TCapacityMeasurement:
        """Get capacity measurement by id."""
        capacity_measurement = self._get_json(
            f"/api/batman/v1/capacityMeasurements/{capacity_measurement_id}",
            timeout=timeout,
        )
        return TCapacityMeasurement(**capacity_measurement)

    def get_capacity_measurements_count_by_battery(
        self,
        battery_id: str,
        api_options: Optional[ApiOptions[TCapacityMeasurementReading]] = None,
        timeout: float = 4.0,
    ) -> int:
        """Get amount of capacity measurement per battery using battery id."""
        filter_by_id = {"battery._id": battery_id}

        if api_options is None:
            api_options = ApiOptions[TCapacityMeasurementReading](filter=filter_by_id)
        else:
            if api_options.filter is not None:
                filter_by_id.update(api_options.filter)
            api_options.filter = filter_by_id

        response = self._get_json(
            "/api/batman/v1/capacityMeasurements/count",
            api_options=api_options,
            timeout=timeout,
        )
        return response  # type: ignore

    def capacity_measurement_exists_on_remote(
        self, capacity_measurement_id: str, timeout: float = 4.0
    ) -> bool:
        """Check capacity measurement on remote."""
        response = self._get_json(
            f"/api/batman/v1/capacityMeasurements/{capacity_measurement_id}",
            timeout=timeout,
        )
        return response["id"] == capacity_measurement_id

    # ********************************************************
    # Section for the Measurements
    # ********************************************************

    def get_latests_measurements(
        self, device_id: str, count: int = 1, timeout: float = 4.0
    ) -> TReadDeviceMeasurementsResult:
        """Get latest live measurement."""
        measurements_list = self._get_json(
            f"/api/time-series/v1/devices/{device_id}/measurements/last/{count}",
            timeout=timeout,
        )

        return TReadDeviceMeasurementsResult(**measurements_list)

    def write_device_measurements(
        self, device_measurements: List[TDeviceMeasurement], timeout: float = 4.0
    ) -> TWriteDeviceMeasurementsResult:
        """Write time series live measurement."""
        write_measurement = self._post_json(
            "/api/time-series/v1/measurements",
            input_data=device_measurements,
            timeout=timeout,
        )
        return TWriteDeviceMeasurementsResult(**write_measurement)

    def read_device_measurements(
        self,
        api_options: Optional[ApiOptions[TReadDeviceMeasurementsFilter]] = None,
        timeout: float = 4.0,
    ) -> TReadDeviceMeasurementsResult:
        """Get time series live measurement."""
        read_measurements = self._get_json(
            "/api/time-series/v1/measurements",
            api_options=api_options,
            timeout=timeout,
        )
        return TReadDeviceMeasurementsResult(**read_measurements)

    def read_device_measurements_by_id(
        self,
        device_id: str,
        selection: str,
        count: int,
        timeout: float = 4.0,
    ) -> TReadDeviceMeasurementsResult:
        """Get time series live measurement by battery id."""

        read_measurements_by_battery_id = self._get_json(
            f"/api/time-series/v1/devices/{device_id}/measurements/{selection}/{count}",
            timeout=timeout,
        )
        return TReadDeviceMeasurementsResult(**read_measurements_by_battery_id)

    # ********************************************************
    # Section for the Reports
    # ********************************************************

    def create_report(self, report: TReportRequired, timeout: float = 4.0) -> TReport:
        """Create report."""
        report_post = self._post_json("/api/batman/v1/reports", report, timeout=timeout)
        return TReport(**report_post)

    def update_report_by_id(
        self, report_id: str, report: TReportReading, timeout: float = 4
    ) -> TReportReading:
        """Update report by id."""
        update_report = self._put_json(
            f"/api/batman/v1/reports/{report_id}", report, timeout=timeout
        )
        return TReportReading(**update_report)

    def get_reports(
        self,
        api_options: Optional[ApiOptions[TReportReading]] = None,
        timeout: float = 4,
    ) -> List[TReport]:
        """Get reports."""
        report_list = self._get_json(
            "/api/batman/v1/reports",
            api_options=api_options,
            timeout=timeout,
        )
        reports = [TReport(**report) for report in report_list]
        return reports

    def get_reports_count(
        self,
        api_options: Optional[ApiOptions[TReportReading]] = None,
        timeout: float = 4,
    ) -> int:
        """Get amount of reports."""
        response = self._get_json(
            "/api/batman/v1/reports/count",
            api_options=api_options,
            timeout=timeout,
        )
        return response  # type: ignore

    def get_reports_count_by_battery(
        self,
        battery: TBatteryReading,
        api_options: Optional[ApiOptions[TReportReading]] = None,
        timeout: float = 4,
    ) -> int:
        """Get amount of reports by battery."""
        filter_with_id = {"origin_id": battery.id}
        if api_options is None:
            api_options = ApiOptions[TReportReading](filter=filter_with_id)
        else:
            if api_options.filter is not None:
                filter_with_id.update(api_options.filter)
            api_options.filter = filter_with_id
        response = self._get_json(
            "/api/batman/v1/reports/count",
            api_options=api_options,
            timeout=timeout,
        )

        return response  # type: ignore

    def get_report_by_id(self, report_id: str, timeout: float = 4) -> TReport:
        """Get reports by id."""
        report = self._get_json(f"/api/batman/v1/reports/{report_id}", timeout=timeout)
        return TReport(**report)

    def get_reports_by_origin_id(
        self,
        origin_id: str,
        api_options: Optional[ApiOptions[TReportReading]] = None,
        timeout: float = 4,
    ) -> List[TReport]:
        """Get reports by origin id."""
        report_list = self._get_json(
            f"/api/batman/v1/reports/byOriginId/{origin_id}",
            api_options=api_options,
            timeout=timeout,
        )

        reports = [TReport(**report) for report in report_list]

        return reports

    def get_reports_by_origin_id_count(
        self,
        origin_id: str,
        api_options: Optional[ApiOptions[TReportReading]] = None,
        timeout: float = 4,
    ) -> int:
        """Get amount of reports by origin id."""
        reports_count = self._get_json(
            f"/api/batman/v1/reports/byOriginId/{origin_id}/count",
            api_options=api_options,
            timeout=timeout,
        )
        return reports_count  # type: ignore

    def remove_report_by_id(self, report_id: str, timeout: float = 4) -> None:
        """Delete reports by id."""
        self._delete_json(
            f"/api/batman/v1/reports/{report_id}",
            timeout=timeout,
        )

    # ********************************************************
    # Section for the userDocs
    # ********************************************************

    def get_user_documents(
        self,
        api_options: Optional[ApiOptions[TUserDocument]] = None,
        timeout: float = 4.0,
    ) -> List[TUserDocument]:
        """Gest user documents"""
        user_documents_list = self._get_json(
            "/api/batman/v1/userDocuments",
            api_options=api_options,
            timeout=timeout,
        )

        user_documents = [TUserDocument(**document) for document in user_documents_list]

        return user_documents

    def get_user_document_by_id(self, user_document_id: str) -> TUserDocument:
        """Get user document by document id."""
        document = self._get_json(f"/api/batman/v1/userDocuments/{user_document_id}")

        return TUserDocument(**document)

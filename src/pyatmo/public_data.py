from typing import Any, Dict

from .auth import NetatmOAuth2
from .exceptions import NoDevice
from .helpers import _BASE_URL, to_time_string

_GETPUBLIC_DATA = _BASE_URL + "api/getpublicdata"

_STATION_TEMPERATURE_TYPE = "temperature"
_STATION_PRESSURE_TYPE = "pressure"
_STATION_HUMIDITY_TYPE = "humidity"

_ACCESSORY_RAIN_LIVE_TYPE = "rain_live"
_ACCESSORY_RAIN_60MIN_TYPE = "rain_60min"
_ACCESSORY_RAIN_24H_TYPE = "rain_24h"
_ACCESSORY_RAIN_TIME_TYPE = "rain_timeutc"
_ACCESSORY_WIND_STRENGTH_TYPE = "wind_strength"
_ACCESSORY_WIND_ANGLE_TYPE = "wind_angle"
_ACCESSORY_WIND_TIME_TYPE = "wind_timeutc"
_ACCESSORY_GUST_STRENGTH_TYPE = "gust_strength"
_ACCESSORY_GUST_ANGLE_TYPE = "gust_angle"


class PublicData:
    def __init__(
        self,
        authData: NetatmOAuth2,
        LAT_NE: str,
        LON_NE: str,
        LAT_SW: str,
        LON_SW: str,
        required_data_type: str = None,  # comma-separated list from above _STATION or _ACCESSORY values
        filtering: bool = False,
    ) -> None:
        self.authData = authData
        postParams: Dict = {
            "lat_ne": LAT_NE,
            "lon_ne": LON_NE,
            "lat_sw": LAT_SW,
            "lon_sw": LON_SW,
            "filter": filtering,
        }

        if required_data_type:
            postParams["required_data"] = required_data_type

        resp = self.authData.post_request(url=_GETPUBLIC_DATA, params=postParams)
        try:
            self.raw_data = resp["body"]
        except (KeyError, TypeError):
            raise NoDevice("No public weather data returned by Netatmo server")

        self.status = resp["status"]
        self.time_exec = to_time_string(resp["time_exec"])
        self.time_server = to_time_string(resp["time_server"])

    def stations_in_area(self) -> int:
        return len(self.raw_data)

    def get_latest_rain(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_RAIN_LIVE_TYPE)

    def get_average_rain(self) -> float:
        return average(self.get_latest_rain())

    def get_60_min_rain(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_RAIN_60MIN_TYPE)

    def get_average_60_min_rain(self) -> float:
        return average(self.get_60_min_rain())

    def get_24_h_rain(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_RAIN_24H_TYPE)

    def get_average_24_h_rain(self) -> float:
        return average(self.get_24_h_rain())

    def get_latest_pressures(self) -> Dict:
        return self.get_latest_station_measures(_STATION_PRESSURE_TYPE)

    def get_average_pressure(self) -> float:
        return average(self.get_latest_pressures())

    def get_latest_temperatures(self) -> Dict:
        return self.get_latest_station_measures(_STATION_TEMPERATURE_TYPE)

    def get_average_temperature(self) -> float:
        return average(self.get_latest_temperatures())

    def get_latest_humidities(self) -> Dict:
        return self.get_latest_station_measures(_STATION_HUMIDITY_TYPE)

    def get_average_humidity(self) -> float:
        return average(self.get_latest_humidities())

    def get_latest_wind_strengths(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_WIND_STRENGTH_TYPE)

    def get_average_wind_strength(self) -> float:
        return average(self.get_latest_wind_strengths())

    def get_latest_wind_angles(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_WIND_ANGLE_TYPE)

    def get_latest_gust_strengths(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_GUST_STRENGTH_TYPE)

    def get_average_gust_strength(self) -> float:
        return average(self.get_latest_gust_strengths())

    def get_latest_gust_angles(self):
        return self.get_accessory_data(_ACCESSORY_GUST_ANGLE_TYPE)

    def get_locations(self) -> Dict:
        locations: Dict = {}
        for station in self.raw_data:
            locations[station["_id"]] = station["place"]["location"]
        return locations

    def get_time_for_rain_measures(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_RAIN_TIME_TYPE)

    def get_time_for_wind_measures(self) -> Dict:
        return self.get_accessory_data(_ACCESSORY_WIND_TIME_TYPE)

    def get_latest_station_measures(self, data_type) -> Dict:
        measures: Dict = {}
        for station in self.raw_data:
            for _, module in station["measures"].items():
                if (
                    "type" in module
                    and data_type in module["type"]
                    and "res" in module
                    and module["res"]
                ):
                    measure_index = module["type"].index(data_type)
                    latest_timestamp = sorted(module["res"], reverse=True)[0]
                    measures[station["_id"]] = module["res"][latest_timestamp][
                        measure_index
                    ]
        return measures

    def get_accessory_data(self, data_type: str) -> Dict[str, Any]:
        data: Dict = {}
        for station in self.raw_data:
            for _, module in station["measures"].items():
                if data_type in module:
                    data[station["_id"]] = module[data_type]
        return data


def average(data: dict) -> float:
    if data:
        return sum(data.values()) / len(data)
    return 0.0

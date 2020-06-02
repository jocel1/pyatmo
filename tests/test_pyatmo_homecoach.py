"""Define tests for HomeCoach module."""
# pylint: disable=protected-access
import json

import pytest

import pyatmo


def test_home_coach_data(home_coach_data):
    assert home_coach_data.default_station == "Bedroom"


@pytest.mark.parametrize(
    "station_id, expected",
    [
        ("12:34:56:26:69:0c", ["Bedroom"]),
        pytest.param(
            "NoValidStation",
            None,
            marks=pytest.mark.xfail(
                reason="Invalid station names are not handled yet."
            ),
        ),
    ],
)
def test_HomeCoachData_get_module_names(homeCoachData, station_id, expected):
    assert sorted(homeCoachData.get_module_names(station_id)) == expected


@pytest.mark.parametrize(
    "station_id, expected",
    [
        (None, {}),
        (
            "12:34:56:26:69:0c",
            {
                "12:34:56:26:69:0c": {
                    "station_name": "Bedroom",
                    "module_name": "Bedroom",
                    "id": "12:34:56:26:69:0c",
                }
            },
        ),
        pytest.param(
            "NoValidStation",
            None,
            marks=pytest.mark.xfail(
                reason="Invalid station names are not handled yet."
            ),
        ),
    ],
)
def test_HomeCoachData_get_modules(homeCoachData, station_id, expected):
    assert homeCoachData.get_modules(station_id) == expected


def test_home_coach_data_no_devices(auth, requests_mock):
    with open("fixtures/home_coach_no_devices.json") as json_file:
        json_fixture = json.load(json_file)
    requests_mock.post(
        pyatmo.home_coach._GETHOMECOACHDATA_REQ,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    with pytest.raises(pyatmo.NoDevice):
        assert pyatmo.home_coach.HomeCoachData(auth)

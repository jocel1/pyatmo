"""Define shared fixtures."""
import json
from contextlib import contextmanager

import pytest

import pyatmo


@contextmanager
def does_not_raise():
    yield


@pytest.fixture(scope="function")
def auth(requests_mock):
    with open("fixtures/oauth2_token.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        pyatmo.auth._AUTH_REQ,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    authorization = pyatmo.ClientAuth(
        clientId="CLIENT_ID",
        clientSecret="CLIENT_SECRET",
        username="USERNAME",
        password="PASSWORD",
        scope=" ".join(pyatmo.auth.ALL_SCOPES),
    )
    return authorization


@pytest.fixture(scope="function")
def homeData(auth, requests_mock):
    with open("fixtures/home_data_simple.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        pyatmo.thermostat._GETHOMESDATA_REQ,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    return pyatmo.HomeData(auth)


@pytest.fixture(scope="function")
def homeStatus(auth, home_id, requests_mock):
    with open("fixtures/home_status_simple.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        pyatmo.thermostat._GETHOMESTATUS_REQ,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    return pyatmo.HomeStatus(auth, home_id)


@pytest.fixture(scope="function")
def publicData(auth, requests_mock):
    with open("fixtures/public_data_simple.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        pyatmo.public_data._GETPUBLIC_DATA,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    return pyatmo.PublicData(auth)


@pytest.fixture(scope="function")
def weatherStationData(auth, requests_mock):
    with open("fixtures/weatherstation_data_simple.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        pyatmo.weather_station._GETSTATIONDATA_REQ,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    return pyatmo.WeatherStationData(auth)


@pytest.fixture(scope="function")
def homeCoachData(auth, requests_mock):
    with open("fixtures/home_coach_simple.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        pyatmo.home_coach._GETHOMECOACHDATA_REQ,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    return pyatmo.HomeCoachData(auth)


@pytest.fixture(scope="function")
def cameraHomeData(auth, requests_mock):
    with open("fixtures/camera_home_data.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        pyatmo.camera._GETHOMEDATA_REQ,
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    for index in ["w", "z", "g"]:
        vpn_url = (
            f"https://prodvpn-eu-2.netatmo.net/restricted/10.255.248.91/"
            f"6d278460699e56180d47ab47169efb31/"
            f"MpEylTU2MDYzNjRVD-LJxUnIndumKzLboeAwMDqTT{index},,"
        )
        with open("fixtures/camera_ping.json") as f:
            json_fixture = json.load(f)
        requests_mock.post(
            vpn_url + "/command/ping",
            json=json_fixture,
            headers={"content-type": "application/json"},
        )
    local_url = "http://192.168.0.123/678460a0d47e5618699fb31169e2b47d"
    with open("fixtures/camera_ping.json") as f:
        json_fixture = json.load(f)
    requests_mock.post(
        local_url + "/command/ping",
        json=json_fixture,
        headers={"content-type": "application/json"},
    )
    return pyatmo.CameraData(auth)

import pytest
import pandas as pd
import requests
from space import SpaceX


@pytest.fixture
def mock_launches_data():
    return [
        {"date_utc": "2008-05-30T19:22:00Z"},
        {"date_utc": "2008-11-15T02:03:00Z"},
        {"date_utc": "2009-05-30T19:22:00Z"},
        {"date_utc": "2012-11-15T02:03:00Z"},
        {"date_utc": "2012-05-30T19:22:00Z"},
        {"date_utc": "2022-11-15T02:03:00Z"},
    ]


@pytest.fixture
def mock_launchpads_data():
    return [
        {"full_name": "site1", "launch_attempts": 10, "launch_successes": 9},
        {"full_name": "site2", "launch_attempts": 11, "launch_successes": 4},
    ]


@pytest.fixture
def mock_get_data(monkeypatch, mock_launches_data, mock_launchpads_data):
    def mock_get_data(self, url):
        if "url1" in url:
            return pd.DataFrame(mock_launchpads_data)
        elif "url2" in url:
            return pd.DataFrame(mock_launches_data)
        else:
            return pd.DataFrame()

    monkeypatch.setattr(SpaceX, "get_data", mock_get_data)


def test_init(mock_get_data):
    spacex = SpaceX(launchpads_url="url1", launches_url="url2")
    assert not spacex.launchpads.empty
    assert not spacex.launches.empty
    assert "date_utc" in spacex.launches.columns


def test_get_data_error(monkeypatch):
    def mock_request(*args, **kwargs):
        raise requests.exceptions.RequestException("Mocked error")

    monkeypatch.setattr(requests, "request", mock_request)

    with pytest.raises(SystemExit):
        spacex = SpaceX()


def test_get_launch_for_year(mock_get_data):
    spacex = SpaceX(launchpads_url="url1", launches_url="url2")
    launch_count = spacex.get_launch_for_year([2008, 2012])
    assert launch_count == {2008: 2, 2012: 2}


def test_get_launch_for_year_outofrange(mock_get_data):
    spacex = SpaceX(launchpads_url="url1", launches_url="url2")
    launch_count = spacex.get_launch_for_year([2008, 2028])
    assert launch_count == {2008: 2}


def test_get_launch_for_year_error(mock_get_data):
    spacex = SpaceX(launchpads_url="url1", launches_url="url2")

    with pytest.raises(ValueError):
        launch_count = spacex.get_launch_for_year([200.5])


def test_get_launch_for_site(mock_get_data):
    spacex = SpaceX(launchpads_url="url1", launches_url="url2")
    launch_count = spacex.get_launch_for_site(["site1", "site2"])
    assert launch_count == {
        "site1": {"launch_attempts": 10, "launch_successes": 9},
        "site2": {"launch_attempts": 11, "launch_successes": 4},
    }


def test_get_launch_for_site_invalid_site(mock_get_data):
    spacex = SpaceX(launchpads_url="url1", launches_url="url2")
    launch_count = spacex.get_launch_for_site(["site1", "somewhere"])
    assert launch_count == {
        "site1": {"launch_attempts": 10, "launch_successes": 9}
    }


def test_get_launch_for_site_error(mock_get_data):
    spacex = SpaceX(launchpads_url="url1", launches_url="url2")
    with pytest.raises(ValueError):
        launch_count = spacex.get_launch_for_site(["site1", 2])

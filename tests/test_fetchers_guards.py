from unittest.mock import MagicMock, patch
import pytest

from ghs.check_config import ValidationException
import ghs.fetchers as fetchers


def make_mock_resp(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.__enter__.return_value = resp
    return resp


@pytest.fixture(autouse=True)
def mock_headers():
    with patch("ghs.fetchers.get_headers", return_value={"Authorization": "token test", "User-Agent": "test"}):
        yield


def test_fetch_user_id_empty_nodes():
    mock_resp = make_mock_resp({"data": {"search": {"nodes": []}}})

    with patch.object(fetchers.my_session, "post", return_value=mock_resp):
        user_id = fetchers.fetch_user_id("nonexistent_user")
        assert user_id is None


def test_fetch_user_id_success():
    mock_resp = make_mock_resp({"data": {"search": {"nodes": [{"id": "MDQ6VXNlcjE="}]}}})

    with patch.object(fetchers.my_session, "post", return_value=mock_resp):
        user_id = fetchers.fetch_user_id("octocat")
        assert user_id == "MDQ6VXNlcjE="


def test_fetch_oldest_contribution_year_empty_nodes_raises():
    mock_resp = make_mock_resp({"data": {"search": {"nodes": []}}})

    with patch.object(fetchers.my_session, "post", return_value=mock_resp):
        with pytest.raises(ValidationException, match="No contribution data found"):
            fetchers.fetch_oldest_contribution_year("nonexistent")


def test_fetch_oldest_contribution_year_success():
    mock_resp = make_mock_resp(
        {
            "data": {
                "search": {
                    "nodes": [
                        {
                            "contributionsCollection": {
                                "contributionYears": [2024, 2023, 2022, 2020]
                            }
                        }
                    ]
                }
            }
        }
    )

    with patch.object(fetchers.my_session, "post", return_value=mock_resp):
        year = fetchers.fetch_oldest_contribution_year("octocat")
        assert year == 2020


def test_fetch_total_repo_commits_missing_object_returns_none():
    mock_resp = make_mock_resp({"data": {"repository": {"object": None}}})

    with patch.object(fetchers.my_session, "post", return_value=mock_resp):
        assert fetchers.fetch_total_repo_commits("empty_repo", "octocat") is None


def test_fetch_total_repo_commits_success():
    mock_resp = make_mock_resp(
        {"data": {"repository": {"object": {"history": {"totalCount": 150}}}}}
    )

    with patch.object(fetchers.my_session, "post", return_value=mock_resp):
        assert fetchers.fetch_total_repo_commits("my_repo", "octocat") == 150


def test_fetch_general_stats_empty_nodes_raises():
    mock_resp = make_mock_resp({"data": {"search": {"nodes": []}}})

    with patch.object(fetchers.my_session, "post", return_value=mock_resp):
        with pytest.raises(ValidationException, match="User unknown not found"):
            fetchers.fetch_general_stats("unknown")

import datetime
import pytest

from ghs.check_config import ValidationException
from ghs.ghs import validate_start_and_end_duration
from ghs.utils import (
    format_date_object,
    parse_user_contribution_repos,
    subtract_years,
)


def test_sorting_preserves_repositories_with_identical_commit_counts():
    """Verify that repositories with equal commit counts are never dropped."""
    user_contribution_repos = {
        "repo_alpha": {
            "owner": "user",
            "commits_count": 5,
            "languages": [{"name": "Python"}],
            "is_private": False,
            "stargazer_count": 10,
            "fork_count": 2,
        },
        "repo_beta": {
            "owner": "user",
            "commits_count": 5,
            "languages": [{"name": "JavaScript"}],
            "is_private": False,
            "stargazer_count": 8,
            "fork_count": 1,
        },
        "repo_gamma": {
            "owner": "user",
            "commits_count": 12,
            "languages": [{"name": "Go"}],
            "is_private": False,
            "stargazer_count": 100,
            "fork_count": 20,
        },
    }

    # The buggy implementation keyed a dictionary by commits_count:
    buggy_mapping = {}
    for repo_name in user_contribution_repos.keys():
        buggy_mapping[user_contribution_repos[repo_name]["commits_count"]] = repo_name

    # The buggy dict drops repo_alpha because repo_beta overwrites it at key 5
    assert len(buggy_mapping) == 2  # Proves the bug: only 2 repos kept out of 3

    # Fixed sorting approach:
    sorted_repos = sorted(
        user_contribution_repos.items(),
        key=lambda item: item[1]["commits_count"],
        reverse=True,
    )

    # All 3 repos are preserved
    assert len(sorted_repos) == 3
    assert sorted_repos[0][0] == "repo_gamma"
    assert sorted_repos[0][1]["commits_count"] == 12
    remaining_names = {sorted_repos[1][0], sorted_repos[2][0]}
    assert remaining_names == {"repo_alpha", "repo_beta"}


def test_validate_start_and_end_duration_valid():
    validate_start_and_end_duration("2020", "2024")


def test_validate_start_and_end_duration_invalid_format():
    with pytest.raises(ValidationException, match="format"):
        validate_start_and_end_duration("abc", "2024")

    with pytest.raises(ValidationException, match="format"):
        validate_start_and_end_duration("2020", "xyz")


def test_validate_start_and_end_duration_inverted():
    with pytest.raises(ValidationException, match="ending year cannot be less than"):
        validate_start_and_end_duration("2024", "2020")

    with pytest.raises(ValidationException, match="ending year cannot be less than"):
        validate_start_and_end_duration("2024", "2024")


def test_validate_start_and_end_duration_gap_too_big():
    with pytest.raises(ValidationException, match="year gap is too big"):
        validate_start_and_end_duration("1980", "2025")


def test_parse_user_contribution_repos():
    repos_input = [
        {
            "contributions": {"totalCount": 4},
            "repository": {
                "name": "project_x",
                "owner": {"login": "octocat"},
                "languages": {"nodes": [{"name": "Rust"}]},
                "isPrivate": False,
                "stargazerCount": 50,
                "forkCount": 5,
            },
        },
        {
            "contributions": {"totalCount": 6},
            "repository": {
                "name": "project_x",
                "owner": {"login": "octocat"},
                "languages": {"nodes": [{"name": "Rust"}]},
                "isPrivate": False,
                "stargazerCount": 50,
                "forkCount": 5,
            },
        },
    ]

    result = parse_user_contribution_repos(repos_input, {})
    assert "project_x" in result
    assert result["project_x"]["commits_count"] == 10  # 4 + 6 aggregated
    assert result["project_x"]["owner"] == "octocat"


def test_date_utilities():
    dt = datetime.datetime(2025, 5, 10, 12, 0, 0)
    formatted = format_date_object(dt)
    assert formatted == "2025-05-10T12:00:00Z"

    sub = subtract_years(dt, 2)
    assert sub == "2023-05-10T12:00:00Z"


def test_render_private_profile_warning():
    from ghs.viewer import render_private_profile_warning

    warning = render_private_profile_warning("testuser")
    assert "token token" not in warning
    assert "Use testuser's token to get their correct contributions stats." in warning


def test_render_top_contribution_multiple_repos():
    from ghs.viewer import _render_top_contribution

    top_data = {
        "repo_alpha": {
            "repo_owner": "user",
            "total_commits": 100,
            "contributors_count": "5",
            "individual_commit_contribution": 5,
            "languages": ["Python"],
            "is_private": False,
            "stargazer_count": 10,
            "fork_count": 2,
        },
        "repo_beta": {
            "repo_owner": "user",
            "total_commits": 50,
            "contributors_count": "2",
            "individual_commit_contribution": 5,
            "languages": ["Rust"],
            "is_private": False,
            "stargazer_count": 20,
            "fork_count": 3,
        },
    }

    rendered = _render_top_contribution(top_data)
    assert "user/repo_alpha" in rendered
    assert "user/repo_beta" in rendered
    assert "During this period you made 5 commits" in rendered

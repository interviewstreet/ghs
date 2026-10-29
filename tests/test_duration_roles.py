from unittest.mock import patch
from ghs.viewer import render_user_summary
from ghs.ghs import user_summary


def test_render_user_summary_without_role():
    output = render_user_summary(
        start_duration="2020",
        end_duration="2021",
        top_contribution_data={},
        output_text="",
        repos={},
        total_commit_contributions=0,
        total_pull_request_contributions=0,
        total_pull_request_review_contributions=0,
    )
    assert "\n2020 - 2021\n" in output
    assert "(" not in output


def test_render_user_summary_with_role():
    output = render_user_summary(
        start_duration="2020",
        end_duration="2021",
        top_contribution_data={},
        output_text="",
        repos={},
        total_commit_contributions=0,
        total_pull_request_contributions=0,
        total_pull_request_review_contributions=0,
        role="Engineering Lead",
    )
    assert "\n2020 - 2021 (Engineering Lead)\n" in output


@patch("ghs.ghs.verify_github_username")
@patch("ghs.ghs.fetch_contribution_collection")
@patch("ghs.ghs.render_user_summary")
@patch("ghs.ghs.render_generated_on", return_value="")
def test_user_summary_extracts_role_metadata(
    mock_render_on, mock_render_summary, mock_fetch, mock_verify
):
    mock_fetch.return_value = ([], 10, 5, 2)
    mock_render_summary.return_value = "rendered"

    # With role
    user_summary("testuser", ["2020-2021:Senior Engineer"], choice=3)
    mock_render_summary.assert_called()
    _, kwargs = mock_render_summary.call_args
    assert kwargs.get("role") == "Senior Engineer"

    # Without role
    mock_render_summary.reset_mock()
    user_summary("testuser", ["2020-2021"], choice=3)
    _, kwargs = mock_render_summary.call_args
    assert kwargs.get("role") is None

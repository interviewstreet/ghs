import inspect
import ghs.utils as utils
import ghs.fetchers as fetchers
import ghs.viewer as viewer
import ghs.check_config as check_config
import ghs.ghs as ghs_cli


def test_utils_functions_have_annotations():
    functions = [
        utils.get_random_user_agent,
        utils.get_headers,
        utils.subtract_years,
        utils.format_date_object,
        utils.let_user_pick,
        utils.parse_user_contribution_repos,
    ]
    for fn in functions:
        annotations = inspect.get_annotations(fn)
        assert len(annotations) > 0, f"{fn.__name__} has no annotations"
        assert "return" in annotations, f"{fn.__name__} has no return annotation"


def test_fetchers_functions_have_annotations():
    functions = [
        fetchers.fetch_oldest_contribution_year,
        fetchers.fetch_contributors_count,
        fetchers.fetch_contribution_collection,
        fetchers.fetch_total_repo_commits,
        fetchers.fetch_general_stats,
        fetchers.fetch_user_id,
    ]
    for fn in functions:
        annotations = inspect.get_annotations(fn)
        assert len(annotations) > 0, f"{fn.__name__} has no annotations"
        assert "return" in annotations, f"{fn.__name__} has no return annotation"


def test_viewer_functions_have_annotations():
    functions = [
        viewer.render_general_stats,
        viewer.render_generated_on,
        viewer.render_private_profile_warning,
        viewer._render_top_contribution,
        viewer.render_user_summary,
    ]
    for fn in functions:
        annotations = inspect.get_annotations(fn)
        assert len(annotations) > 0, f"{fn.__name__} has no annotations"
        assert "return" in annotations, f"{fn.__name__} has no return annotation"


def test_check_config_functions_have_annotations():
    functions = [
        check_config.config_dir_path,
        check_config.config_file_path,
        check_config.check_config_dir,
        check_config.create_config_file,
        check_config.fetch_token_scopes,
        check_config.validate_token_scopes,
        check_config.save_token,
        check_config.get_saved_token,
    ]
    for fn in functions:
        annotations = inspect.get_annotations(fn)
        assert len(annotations) > 0, f"{fn.__name__} has no annotations"
        assert "return" in annotations, f"{fn.__name__} has no return annotation"


def test_ghs_cli_functions_have_annotations():
    functions = [
        ghs_cli.verify_github_username,
        ghs_cli.general_stats,
        ghs_cli.validate_start_and_end_duration,
        ghs_cli.user_summary,
        ghs_cli.main_proxy,
    ]
    for fn in functions:
        annotations = inspect.get_annotations(fn)
        assert len(annotations) > 0, f"{fn.__name__} has no annotations"
        assert "return" in annotations, f"{fn.__name__} has no return annotation"

import colorama
from termcolor import cprint
import datetime

colorama.init()


def render_general_stats(username, general_stats, spinner):
    total_prs = general_stats["pullRequests"]["totalCount"]
    total_contribution = general_stats["repositoriesContributedTo"]["totalCount"]
    total_repositories = general_stats["repositories"]["totalCount"]
    all_repositories = general_stats["repositories"]["nodes"]
    total_issues = (
        general_stats["openIssues"]["totalCount"]
        + general_stats["closedIssues"]["totalCount"]
    )

    total_stars, total_forks, total_releases, total_packages = [0, 0, 0, 0]
    for repo in all_repositories:
        total_stars += repo["stargazers"]["totalCount"]
        total_forks += repo["forks"]["totalCount"]
        total_packages += repo["packages"]["totalCount"]
        total_releases += repo["releases"]["totalCount"]

    spinner.stop()

    text = f"\nGithub stats of {username}\n"
    cprint(text, "cyan", end="")
    output_text = text

    text = f"\nTotal PRs: {total_prs}\nContributed to: {total_contribution}\nTotal Issues: {total_issues}\nTotal Repositories: {total_repositories}\nTotal Stars: {total_stars}\nTotal Forks: {total_forks}\nTotal Packages: {total_packages}\nTotal Releases: {total_releases}\n"
    print(text, end="")
    output_text += text

    if (
        total_prs
        + total_contribution
        + total_issues
        + total_repositories
        + total_stars
        + total_forks
        + total_packages
        + total_releases
        == 0
    ):
        output_text += render_private_profile_warning(username)

    output_text += render_generated_on()

    return output_text


def render_generated_on():
    today = datetime.datetime.now().strftime("%d-%b-%Y")
    text = f"\ngenerated on: {today}"
    cprint(text, "green")
    return text


def render_private_profile_warning(username):
    text = f"\nIt's possible that {username} has made their contributions private. Use {username}'s token token to get their correct contributions stats."
    cprint(text, "yellow")
    return text


def _render_top_contribution(top_contribution_data):
    text = f"\nYour Top Contributions:\n"
    print(text)
    output_text = text
    count = 0
    for i in top_contribution_data.keys():
        count += 1
        if count > 3:
            break
        repo_name = i
        repo_owner = top_contribution_data[i]["repo_owner"]
        total_commits = top_contribution_data[i]["total_commits"]
        contributors_count = top_contribution_data[i]["contributors_count"]
        individual_commit_countribution = top_contribution_data[i][
            "individual_commit_contribution"
        ]
        languages = top_contribution_data[i]["languages"]
        is_private = top_contribution_data[i]["is_private"]
        stargazer_count = top_contribution_data[i]["stargazer_count"]
        fork_count = top_contribution_data[i]["fork_count"]

        text = f"{count}.) "
        print(text, end="")
        output_text += text

        if is_private:
            text = f"private repo belonging to {repo_owner}\n"
            cprint(text, "green", end="")
            output_text += text
        else:
            text = f"{repo_owner}/{repo_name}\n"
            cprint(text, "green", end="")
            output_text += text

        if total_commits is not None:
            text = f"\t * This repository has a total of {total_commits} commits{f' and {contributors_count} contributors' if contributors_count is not None else ''}.\n"
            print(text, end="")
            output_text += text
        if stargazer_count > 0:
            text = f"\t * It has {stargazer_count} stars{f' and {fork_count} forks' if fork_count > 0 else ''}.\n"
            print(text, end="")
            output_text += text

        text = f"\t * During this period you made {individual_commit_countribution} commits to this repo.\n\t * Top languages of the repo {languages}.\n"
        print(text, end="")
        output_text += text

    return output_text


def render_user_summary(
    start_duration,
    end_duration,
    top_contribution_data,
    output_text,
    repos,
    total_commit_contributions,
    total_pull_request_contributions,
    total_pull_request_review_contributions,
):
    text = f"\n{start_duration} - {end_duration}\n"
    output_text += text
    cprint(text, color="cyan")
    if total_commit_contributions == 0:
        text = "No public code contribution during this period\n"
        print(text, end="")
        output_text += text
    else:
        text = "During this period, you made a total of "
        print(text, end="")
        output_text += text

        text = f"{total_pull_request_contributions} Pull requests"
        cprint(text, "yellow", end="")
        output_text += text

        text = " and "
        print(text, end="")
        output_text += text

        text = f"{total_commit_contributions} commits "
        cprint(text, "yellow", end="")
        output_text += text

        text = f"across {len(repos) if len(repos) < 100 else '100+'} repositories.\n"
        print(text, end="")
        output_text += text
        if total_pull_request_review_contributions > 0:
            text = "You also "
            print(text, end="")
            output_text += text

            text = (
                f"reviewed {total_pull_request_review_contributions} pull requests.\n"
            )
            cprint(text, "yellow", end="")
            output_text += text

        output_text += _render_top_contribution(top_contribution_data)

    return output_text

import argparse
import datetime
import traceback

import colorama
import pyperclip
from halo import Halo
from termcolor import cprint

from ghs.__init__ import __version__
from ghs.check_config import ValidationException, check_config_dir, save_token
from ghs.fetchers import (
    fetch_contribution_collection,
    fetch_contributors_count,
    fetch_general_stats,
    fetch_oldest_contribution_year,
    fetch_total_repo_commits,
    fetch_user_id,
)
from ghs.utils import (
    format_date_object,
    let_user_pick,
    parse_user_contribution_repos,
    subtract_years,
)
from ghs.viewer import render_general_stats, render_generated_on, render_user_summary

colorama.init()
spinner = Halo(text="Loading", spinner="dots")


def verify_github_username(username):
    if fetch_user_id(username) is None:
        raise ValidationException(f"Error: {username} is not a valid github username")
    spinner.stop()


def general_stats(username):
    spinner.start()
    verify_github_username(username)
    spinner.start()
    general_stats = fetch_general_stats(username)
    return render_general_stats(username, general_stats, spinner)


def validate_start_and_end_duration(start_duration, end_duration):
    if not start_duration.isdigit() or not end_duration.isdigit():
        raise ValidationException("Error: duration not provided in the desired format")

    if int(end_duration) <= int(start_duration):
        raise ValidationException(
            "Error: ending year cannot be less than starting year"
        )

    if int(end_duration) - int(start_duration) > 30:
        raise ValidationException("Error: the year gap is too big")


def user_summary(username, durations, choice):
    text = ""
    if choice == 1:
        text = f"\nGithub summary of {username} for the past 12 months.\n"
    elif choice == 2:
        text = f"\nGithub summary of {username} since joining.\n"
    elif choice == 3:
        text = f"\nGithub summary of {username}\n"

    cprint(text, "magenta", end="")
    # output_text is used to collect the text in a single string
    # so that it can be copied to clipboard if the flag is provided
    output_text = text

    if choice != 2:
        spinner.start()
        verify_github_username(username)

    for duration in durations:
        spinner.start()
        duration = duration.strip()
        if choice == 1:
            start_duration, end_duration = duration.split("#")
        elif choice == 2 or choice == 3:
            try:
                start_duration, end_duration = duration.split("-")
            except Exception:
                raise ValidationException(
                    "Error: duration not provided in the desired format"
                )

        start_duration = start_duration.strip()
        end_duration = end_duration.strip()
        if end_duration == "present" and choice is not 1:
            end_duration = f"{datetime.date.today().year + 1}"

        (
            total_commit_contributions,
            total_pull_request_contributions,
            total_pull_request_review_contributions,
        ) = [0, 0, 0]
        user_contribution_repos, top_contribution_data = [{}, {}]

        if choice == 1:
            contribution_collection = [
                repos,
                total_commit_contributions,
                total_pull_request_contributions,
                total_pull_request_review_contributions,
            ] = fetch_contribution_collection(username, start_duration)

            user_contribution_repos = parse_user_contribution_repos(
                repos[:5], user_contribution_repos
            )
        elif choice == 2 or choice == 3:
            validate_start_and_end_duration(start_duration, end_duration)

            for curr_year in range(int(start_duration), int(end_duration)):
                start_date = format_date_object(datetime.datetime(curr_year, 1, 1))
                (
                    repos,
                    commit_contributions,
                    pull_request_contributions,
                    pull_request_review_contributions,
                ) = fetch_contribution_collection(username, start_date)

                total_commit_contributions += commit_contributions
                total_pull_request_contributions += pull_request_contributions
                total_pull_request_review_contributions += (
                    pull_request_review_contributions
                )

                user_contribution_repos = parse_user_contribution_repos(
                    repos[:5], user_contribution_repos
                )

            contribution_collection = [
                repos,
                total_commit_contributions,
                total_pull_request_contributions,
                total_pull_request_review_contributions,
            ]

        commit_count_repo_name_mapping = {}
        for repo_name in user_contribution_repos.keys():
            commit_count_repo_name_mapping[
                user_contribution_repos[repo_name]["commits_count"]
            ] = repo_name

        sorted_commit_counts = sorted(
            list(commit_count_repo_name_mapping.keys()), reverse=True
        )

        for commits_count in sorted_commit_counts:
            repo_name = commit_count_repo_name_mapping[commits_count]
            repo = user_contribution_repos[repo_name]
            repo_owner, languages, is_private, stargazer_count, fork_count = (
                repo["owner"],
                repo["languages"],
                repo["is_private"],
                repo["stargazer_count"],
                repo["fork_count"],
            )

            parsed_languages = []
            for l in languages:
                parsed_languages.append(l["name"])

            total_commits = fetch_total_repo_commits(repo_name, repo_owner)
            contributors_count = fetch_contributors_count(repo_owner, repo_name)

            top_contribution_data[repo_name] = {
                "repo_owner": repo_owner,
                "total_commits": total_commits,
                "contributors_count": contributors_count,
                "individual_commit_contribution": commits_count,
                "languages": parsed_languages,
                "is_private": is_private,
                "stargazer_count": stargazer_count,
                "fork_count": fork_count,
            }

        spinner.stop()
        if end_duration == f"{datetime.date.today().year + 1}":
            end_duration = "present"
        if choice == 1:
            start_duration = start_duration.split("T")[0]

        output_text = render_user_summary(
            start_duration,
            end_duration,
            top_contribution_data,
            output_text,
            *contribution_collection,
        )

    output_text += render_generated_on()
    return output_text


def main():
    parser = argparse.ArgumentParser(
        description="Get stats and summary of your github profile."
    )

    parser.add_argument(
        "-v", "--version", action="store_true", help="print cli version and exit"
    )

    parser.add_argument(
        "-t",
        "--token-update",
        dest="token_update",
        action="store_true",
        help="update the token in config and exit",
    )

    parser.add_argument(
        "-u", dest="username", metavar="<username>", help="github username"
    )

    parser.add_argument(
        "-s",
        "--summary",
        dest="summary",
        action="store_true",
        help="display the summary of user's github profile",
    )

    parser.add_argument(
        "-c",
        "--copy-to-clipboard",
        dest="copy_to_clipboard",
        action="store_true",
        help="copy the output to clipboard",
    )

    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit(0)

    if args.token_update:
        if not check_config_dir(spinner):
            exit(1)
        else:
            save_token()
        exit(0)

    if args.username:
        if not check_config_dir(spinner):
            exit(1)
        if args.summary:
            choice = None
            while choice is None:
                choice = let_user_pick(
                    [
                        "Generate the summary for the past 12 months",
                        "Generate the summary from when you joined github",
                        "Custom durations",
                    ]
                )

            if choice == 1:
                durations = f"{subtract_years(datetime.datetime.now(), 1)}#present"
            elif choice == 2:
                spinner.start()
                verify_github_username(args.username)
                year = fetch_oldest_contribution_year(args.username)
                durations = ""
                for val in list(range(year, datetime.date.today().year + 1)):
                    if val == datetime.date.today().year:
                        durations += f"{val}-present"
                    else:
                        durations += f"{val}-{val+1},"
            elif choice == 3:
                durations = input(
                    "Enter year duration in this format -> 2017-2019,2019-2021,2021-present: "
                )

            output_text = user_summary(args.username, durations.split(","), choice)
            if args.copy_to_clipboard:
                pyperclip.copy(output_text)
        else:
            output_text = general_stats(args.username)
            if args.copy_to_clipboard:
                pyperclip.copy(output_text)
    else:
        raise ValidationException("Error: username not provided")


def main_proxy():
    try:
        main()
    except ValidationException as e:
        spinner.stop()
        cprint(e, color="red", attrs=["bold"])
    except KeyboardInterrupt:
        cprint("\nExiting", color="yellow")
    except Exception as e:
        spinner.stop()
        cprint(f"Error: {e}", color="red", attrs=["bold"])
        traceback_str = "".join(traceback.format_tb(e.__traceback__))
        print(f"Traceback: \n{traceback_str}")

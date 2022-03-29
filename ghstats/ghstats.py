import argparse
import datetime

import colorama
import requests
from halo import Halo
from requests import Session
from retry_requests import retry
from termcolor import cprint

from ghstats.__init__ import __version__
from ghstats.check_config import check_config_dir, save_token
from ghstats.es_queries import (contribution_collection_query,
                                contribution_years_query, general_stats_query,
                                total_commit_query)
from ghstats.utils import (format_date_object, get_headers, let_user_pick,
                           subtract_years)

colorama.init()
my_session = retry(Session(), retries=2, backoff_factor=10)
spinner = Halo(text='Loading', spinner='dots')


def fetch_contributors_count(repo_owner, repo_name, headers):
  resp = requests.get(
      f'https://api.github.com/repos/{repo_owner}/{repo_name}/contributors?per_page=1&anon=true', headers=headers)
  if 'Link' in resp.headers.keys():
    link = resp.headers['Link']
    link = link.split(',')[1].strip()
    link = link[link.find("&page="):]
    count = link[link.find("=")+1: link.find(">")]
    return count
  else:
    return None


def fetch_contribution_collection(username, headers, start_date):
  with my_session.post('https://api.github.com/graphql', json={'query': contribution_collection_query(username, start_date)}, headers=headers) as result:
    request = result

  if request.status_code == 200:
    result = request.json()

  contribution_collection = result['data']['search']['nodes'][0]['contributionsCollection']
  repos = contribution_collection['commitContributionsByRepository']
  total_commit_contributions = contribution_collection['totalCommitContributions']
  total_pull_request_contributions = contribution_collection['totalPullRequestContributions']
  total_pull_request_review_contributions = contribution_collection['totalPullRequestReviewContributions']

  return [repos, total_commit_contributions, total_pull_request_contributions, total_pull_request_review_contributions]


def fetch_total_repo_commits(repo_name, repo_owner, headers):
  with my_session.post('https://api.github.com/graphql', json={'query': total_commit_query(repo_name, repo_owner)}, headers=headers) as result:
    request = result

  if request.status_code == 200:
    result = request.json()

  if result['data']['repository']['object'] == None:
    return None

  return result['data']['repository']['object']['history']['totalCount']


def parse_repos(repos, user_contribution_repos):
  for repo in repos[:5]:
    commits_count = repo['contributions']['totalCount']
    repo_name = repo['repository']['name']
    repo_owner = repo['repository']['owner']['login']
    languages = repo['repository']['languages']['nodes']
    is_private = repo['repository']['isPrivate']
    stargazer_count = repo['repository']['stargazerCount']
    fork_count = repo['repository']['forkCount']

    if repo_name in user_contribution_repos.keys():
      user_contribution_repos[repo_name]['commits_count'] += commits_count
    else:
      user_contribution_repos[repo_name] = {'owner': repo_owner, 'commits_count': commits_count,
                                            'languages': languages, 'is_private': is_private, 'stargazer_count': stargazer_count, 'fork_count': fork_count}

  return user_contribution_repos


def print_top_contribution(final_data):
  print(f"\nYour Top Contributions:\n")
  count = 0
  for i in final_data.keys():
    count += 1
    if count > 3:
      break
    repo_name = i
    repo_owner = final_data[i]['repo_owner']
    total_commits = final_data[i]['total_commits']
    contributors_count = final_data[i]['contributors_count']
    individual_commit_countribution = final_data[i]['individual_commit_contribution']
    languages = final_data[i]['languages']
    is_private = final_data[i]['is_private']
    stargazer_count = final_data[i]['stargazer_count']
    fork_count = final_data[i]['fork_count']

    if is_private:
      print(f"{count}.) private repo belonging to {repo_owner}")
    else:
      print(f"{count}.) {repo_owner}/{repo_name}")

    if total_commits is not None:
      print(
          f"\t * This repository has a total of {total_commits} commits{f' and {contributors_count} contributors' if contributors_count is not None else ''}.")
    if stargazer_count > 0:
      print(
          f"\t * It has {stargazer_count} stars{f' and {fork_count} forks' if fork_count > 0 else ''}.")
    print(
        f"\t * During this period you made {individual_commit_countribution} commits to this repo.")
    print(
        f"\t * Top languages of the repo {languages}.")


def get_user_highlights(username, headers, durations, choice):
  for duration in durations:
    spinner.start()
    duration = duration.strip()
    if choice == 2:
      start_duration, end_duration = duration.split('#')
    elif choice == 1 or choice == 3:
      start_duration, end_duration = duration.split('-')

    start_duration = start_duration.strip()
    end_duration = end_duration.strip()
    if end_duration == 'present' and choice is not 2:
      end_duration = datetime.date.today().year + 1

    total_commit_contributions = 0
    total_pull_request_review_contributions = 0
    total_pull_request_contributions = 0
    user_contribution_repos = {}
    final_data = {}

    if choice == 2:
      repos, total_commit_contributions, total_pull_request_contributions, total_pull_request_review_contributions = fetch_contribution_collection(
          username, headers, start_duration)

      user_contribution_repos = parse_repos(repos[:5], user_contribution_repos)
    elif choice == 1 or choice == 3:
      for curr_year in range(int(start_duration), int(end_duration)):
        start_date = format_date_object(datetime.datetime(curr_year, 1, 1))
        repos, commit_contributions, pull_request_contributions, pull_request_review_contributions = fetch_contribution_collection(
            username, headers, start_date)

        total_commit_contributions += commit_contributions
        total_pull_request_contributions += pull_request_contributions
        total_pull_request_review_contributions += pull_request_review_contributions

        user_contribution_repos = parse_repos(repos[:5], user_contribution_repos)

    commit_count_repo_name_mapping = {}
    for repo_name in user_contribution_repos.keys():
      commit_count_repo_name_mapping[user_contribution_repos[repo_name]
                                     ['commits_count']] = repo_name

    sorted_commit_counts = sorted(list(commit_count_repo_name_mapping.keys()), reverse=True)

    for commits_count in sorted_commit_counts:
      repo_name = commit_count_repo_name_mapping[commits_count]
      repo = user_contribution_repos[repo_name]
      repo_owner, languages, is_private, stargazer_count, fork_count = repo['owner'], repo[
          'languages'], repo['is_private'], repo['stargazer_count'], repo['fork_count']

      parsed_languages = []
      for l in languages:
        parsed_languages.append(l['name'])

      total_commits = fetch_total_repo_commits(repo_name, repo_owner, headers)
      contributors_count = fetch_contributors_count(repo_owner, repo_name, headers=get_headers())

      final_data[repo_name] = {'repo_owner': repo_owner, 'total_commits': total_commits, 'contributors_count': contributors_count,
                               'individual_commit_contribution': commits_count, 'languages': parsed_languages, 'is_private': is_private, 'stargazer_count': stargazer_count, 'fork_count': fork_count}

    spinner.stop()
    if end_duration == datetime.date.today().year + 1:
      end_duration = 'present'
    if choice == 2:
      start_duration = start_duration.split('T')[0]

    cprint(f"\n{start_duration} - {end_duration}\n", color="green")

    print(
        f"During this period, you made a total of {total_pull_request_contributions} Pull requests and {total_commit_contributions} commits accross {len(repos) if len(repos) < 100 else '100+'} repositories.")
    if (total_pull_request_review_contributions > 0):
      print(
          f"You also reviewed {total_pull_request_review_contributions} pull requests.")

    print_top_contribution(final_data)


def get_general_stats(username, headers):
  spinner.start()
  with my_session.post('https://api.github.com/graphql', json={'query': general_stats_query(username)}, headers=headers) as result:
    request = result

  if request.status_code == 200:
    result = request.json()
    user_details = result['data']['search']['nodes'][0]

    total_prs = user_details['pullRequests']['totalCount']
    total_contribution = user_details['repositoriesContributedTo']['totalCount']
    total_repositories = user_details['repositories']['totalCount']
    all_repositories = user_details['repositories']['nodes']
    total_issues = user_details['openIssues']['totalCount'] + \
        user_details['closedIssues']['totalCount']

    total_stars = total_forks = total_releases = total_packages = 0
    for repo in all_repositories:
      total_stars += repo['stargazers']['totalCount']
      total_forks += repo['forks']['totalCount']
      total_packages += repo['packages']['totalCount']
      total_releases += repo['releases']['totalCount']

    spinner.stop()

    output_text = f"\nTotal PRs: {total_prs}\nContributed to: {total_contribution}\nTotal Issues: {total_issues}\nTotal Repositories: {total_repositories}\nTotal Stars: {total_stars}\nTotal Forks: {total_forks}\nTotal Packages: {total_packages}\nTotal Releases: {total_releases}"
    return output_text
  else:
    raise Exception("Query to return details of Username Failed {}".format(request.status_code))


def get_oldest_contribution_year(username, headers):
  with my_session.post('https://api.github.com/graphql', json={'query': contribution_years_query(username)}, headers=headers) as result:
    spinner.stop()
    request = result

  if request.status_code == 200:
    result = request.json()
    return result['data']['search']['nodes'][0]['contributionsCollection']['contributionYears'][-1]
  else:
    return None


def main():
  parser = argparse.ArgumentParser(description="Get stats and highlights of your github profile.")

  # add arguments to our CLI
  parser.add_argument(
      "-v", "--version", action="store_true", help="print cli version and exit"
  )

  parser.add_argument(
      "-u", dest="username", metavar="<username>", help="github username"
  )

  parser.add_argument(
      "-t", "--token-update", dest="token_update", action="store_true", help="update the token in the config"
  )

  parser.add_argument(
      "--highlights", dest="highlights", action="store_true", help="display the highlights of user's github profile"
  )

  args = parser.parse_args()

  if args.version:
    print(__version__)
    exit(0)

  if args.token_update:
    save_token()
    exit(0)

  if args.username:
    if not check_config_dir(spinner):
      exit(1)
    if args.highlights:
      choice = None
      while choice is None:
        choice = let_user_pick(['Get the highlights from when you joined github',
                                'Get the hightlights for the past 12 months', 'Custom durations'])

      if choice == 1:
        year = get_oldest_contribution_year(args.username, get_headers())
        durations = ""
        for val in list(range(year, datetime.date.today().year + 1)):
          if (val == datetime.date.today().year):
            durations += f"{val}-present"
          else:
            durations += f"{val}-{val+1},"
      elif choice == 2:
        durations = f"{subtract_years(datetime.datetime.now(), 1)}#present"
      elif choice == 3:
        durations = input(
            "Enter year duration in this format -> 2017-2019,2019-2021,2021-present: ")

      get_user_highlights(args.username, get_headers(), durations.split(','), choice)
    else:
      output_text = get_general_stats(args.username, get_headers())
      print(output_text)
  else:
    cprint(
        "Error: username not provided",
        color="red",
        attrs=["bold"],
    )
    spinner.stop()


if __name__ == "__main__":
  main()

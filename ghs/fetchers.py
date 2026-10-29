import requests
from requests import Session
from retry_requests import retry

from ghs.check_config import ValidationException
from ghs.es_queries import (
    contribution_collection_query,
    contribution_years_query,
    general_stats_query,
    total_commit_query,
    user_id_query,
)
from ghs.utils import get_headers

my_session = retry(Session(), retries=2, backoff_factor=10)


def fetch_oldest_contribution_year(username):
    with my_session.post(
        "https://api.github.com/graphql",
        json={"query": contribution_years_query(username)},
        headers=get_headers(),
    ) as result:
        request = result

    if request.status_code == 200:
        result = request.json()
        nodes = result.get("data", {}).get("search", {}).get("nodes", [])
        if not nodes:
            raise ValidationException(f"No contribution data found for user {username}")
        years = (
            nodes[0]
            .get("contributionsCollection", {})
            .get("contributionYears", [])
        )
        if not years:
            raise ValidationException(f"No contribution years found for user {username}")
        return years[-1]
    else:
        raise Exception(f"Query failed with status code: {request.status_code}")


def fetch_contributors_count(repo_owner, repo_name):
    resp = requests.get(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors?per_page=1&anon=true",
        headers=get_headers(),
    )
    if "Link" in resp.headers.keys():
        link = resp.headers["Link"]
        link = link.split(",")[1].strip()
        link = link[link.find("&page=") :]
        count = link[link.find("=") + 1 : link.find(">")]
        return count
    else:
        return None


def fetch_contribution_collection(username, start_date):
    with my_session.post(
        "https://api.github.com/graphql",
        json={"query": contribution_collection_query(username, start_date)},
        headers=get_headers(),
    ) as result:
        request = result

    if request.status_code != 200:
        raise Exception(f"Query failed with status code: {request.status_code}")

    result = request.json()
    nodes = result.get("data", {}).get("search", {}).get("nodes", [])
    if not nodes:
        raise ValidationException(
            f"No contribution collection found for user {username}"
        )

    contribution_collection = nodes[0].get("contributionsCollection", {})
    repos = contribution_collection.get("commitContributionsByRepository", [])
    total_commit_contributions = contribution_collection.get(
        "totalCommitContributions", 0
    )
    total_pull_request_contributions = contribution_collection.get(
        "totalPullRequestContributions", 0
    )
    total_pull_request_review_contributions = contribution_collection.get(
        "totalPullRequestReviewContributions", 0
    )

    return [
        repos,
        total_commit_contributions,
        total_pull_request_contributions,
        total_pull_request_review_contributions,
    ]


def fetch_total_repo_commits(repo_name, repo_owner):
    with my_session.post(
        "https://api.github.com/graphql",
        json={"query": total_commit_query(repo_name, repo_owner)},
        headers=get_headers(),
    ) as result:
        request = result

    if request.status_code != 200:
        return None

    result = request.json()
    repo = (
        result.get("data", {}).get("repository")
        if isinstance(result, dict)
        else None
    )
    if not repo or not repo.get("object"):
        return None

    return repo["object"].get("history", {}).get("totalCount")


def fetch_general_stats(username):
    with my_session.post(
        "https://api.github.com/graphql",
        json={"query": general_stats_query(username)},
        headers=get_headers(),
    ) as result:
        request = result

    if request.status_code == 200:
        result = request.json()
        nodes = result.get("data", {}).get("search", {}).get("nodes", [])
        if not nodes:
            raise ValidationException(f"User {username} not found")
        return nodes[0]
    else:
        raise Exception(f"Query failed with status code: {request.status_code}")


def fetch_user_id(username):
    with my_session.post(
        "https://api.github.com/graphql",
        json={"query": user_id_query(username)},
        headers=get_headers(),
    ) as result:
        request = result

    if request.status_code == 200:
        result = request.json()
        nodes = result.get("data", {}).get("search", {}).get("nodes", [])
        if not nodes:
            return None
        return nodes[0].get("id")
    else:
        raise Exception(f"Query failed with status code: {request.status_code}")

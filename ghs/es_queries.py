def general_stats_query(username):
    query = """{
    search(query: USERNAME, type: USER, first: 10) {
      nodes {
        ... on User {
          id
          email
          name
          pullRequests(first: 1) {
            totalCount
          }
          repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
            totalCount
          }
          openIssues: issues(states: OPEN) {
            totalCount
          }
          closedIssues: issues(states: CLOSED) {
            totalCount
          }
          packages(first: 100) {
            nodes {
              statistics {
                downloadsTotalCount
              }
              name
            }
          }
          repositories(
            first: 100
            ownerAffiliations: OWNER
            orderBy: {field: STARGAZERS, direction: DESC}
          ) {
            totalCount
            nodes {
              stargazers {
                totalCount
              }
              releases {
                totalCount
              }
              packages {
                totalCount
              }
              forks {
                totalCount
              }
            }
          }
        }
      }
    }
  }
  """.replace(
        "USERNAME", '"{}"'.format(username)
    )

    return query


def contribution_years_query(username):
    query = """{
    search(query: USERNAME, type: USER, first: 1) {
      nodes {
        ... on User {
          contributionsCollection {
            contributionYears
          }
        }
      }
    }
  }""".replace(
        "USERNAME", '"{}"'.format(username)
    )

    return query


def contribution_collection_query(username, date):
    query = """{
    search(query: USERNAME, type: USER, first: 1) {
      nodes {
        ... on User {
          contributionsCollection(from: DATE) {
            totalCommitContributions
            totalPullRequestContributions
            totalPullRequestReviewContributions
            commitContributionsByRepository(maxRepositories: 100) {
              contributions(orderBy: {field: COMMIT_COUNT, direction: DESC}) {
                totalCount
              }
              repository {
                languages(orderBy: {field: SIZE, direction: DESC}, first: 3) {
                  nodes {
                    name
                  }
                }
                name
                owner {
                  login
                }
                stargazerCount
                forkCount
                isPrivate
              }
            }
          }
        }
      }
    }
  }
  """.replace(
        "USERNAME", '"{}"'.format(username)
    ).replace(
        "DATE", '"{}"'.format(date)
    )

    return query


def total_commit_query(NAME, OWNER):
    query = """
      {
        repository(name: NAME, owner: OWNER) {
          object(expression: "master") {
            ... on Commit {
              id
              history {
                totalCount
              }
            }
          }
        }
      }
  """.replace(
        "NAME", '"{}"'.format(NAME)
    ).replace(
        "OWNER", '"{}"'.format(OWNER)
    )

    return query


def viewer_query():
    query = """{
        viewer {
          login
        }
      }"""

    return query


def user_id_query(username):
    query = """{
    search(query: NAME, type: USER, first: 1) {
      nodes {
        ... on User {
          id
        }
      }
    }
  }
  """.replace(
        "NAME", '"{}"'.format(username)
    )

    return query

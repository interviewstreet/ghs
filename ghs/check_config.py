import configparser
import os
import requests

import colorama
from halo import Halo
from requests import Session
from retry_requests import retry
from termcolor import cprint

from ghs.es_queries import viewer_query

colorama.init()
home_dir = os.path.expanduser("~")
config = configparser.ConfigParser()
spinner = Halo(text="Checking if the token is valid", spinner="dots")
my_session = retry(Session(), retries=2, backoff_factor=10)


def config_dir_path():
    return os.path.join(home_dir, ".ghs")


def config_file_path():
    return os.path.join(config_dir_path(), "ghs.config")


class ValidationException(Exception):
    pass


def check_config_dir(spnr):
    try:
        path = config_dir_path()
        # makes path recursively. returns None if already exist.
        os.makedirs(path, exist_ok=True)
        if not os.path.isfile(os.path.join(path, "ghs.config")):
            spnr.stop()
            return create_config_file()
    except IOError:
        print("Error occured while creating config files.")

    return True


def create_config_file():
    cprint(
        "Creating config file",
        color="green",
    )

    return save_token()


# TODO: move this to fetchers after resolving circular imports
def fetch_token_scopes(headers):
    resp = requests.get(f"https://api.github.com/rate_limit", headers=headers)

    if "X-OAuth-Scopes" in resp.headers.keys():
        scopes = resp.headers["X-OAuth-Scopes"]
        return scopes.split(", ")
    else:
        return None


def validate_token_scopes(headers):
    required_scopes = ["read:user", "repo", "read:packages"]
    token_scopes = fetch_token_scopes(headers)
    if token_scopes is None or not set(required_scopes).issubset(token_scopes):
        raise ValidationException(
            f"Error: The token does not have valid scopes. \n Required scopes: {required_scopes}. \n Provided token scopes: {token_scopes} "
        )


def save_token():
    pat = input("please enter your github pat: ")

    headers = {
        "Authorization": f"token {pat}",
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
    }

    spinner.start()
    with my_session.post(
        "https://api.github.com/graphql",
        json={"query": viewer_query()},
        headers=headers,
    ) as result:
        request = result
    spinner.stop()

    if request.status_code == 200:
        result = request.json()
        username = result["data"]["viewer"]["login"]
        validate_token_scopes(headers)
        print(f"Saving the token for {username} in ~/.ghs/ghs.config")
        config["TOKEN"] = {"pat": pat}
        with open(config_file_path(), "w") as f:
            config.write(f)
        return True
    elif request.status_code == 401:
        raise ValidationException("The PAT is not valid")
    else:
        raise ValidationException("Error in saving the pat")


def get_saved_token():
    config.read(config_file_path())
    return config["TOKEN"]["pat"]

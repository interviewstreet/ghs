# ghs

CLI tool to get your Github profile's stats and summary.

## Installation

The stable version of this package is maintained on pypi, install using pip:

```bash
pip install ghs
```

## PAT

Generate a Github personal access token (https://github.com/settings/tokens) and use the `ghs -t` command to save it in the config file. This will make sure that your private contributions are also considered while generating the stats and the summary.

## Usage

```
➜ ghs -h
usage: ghs [-h] [-v] [-t] [-u <username>] [--highlights] [-c]

Get stats and highlights of your github profile.

optional arguments:
  -h, --help               show this help message and exit
  -v, --version            print cli version and exit
  -t, --token-update       update the token in config and exit
  -u <username>            github username
  --highlights             display the highlights of user's github profile
  -c, --copy-to-clipboard  copy the output to clipboard
```

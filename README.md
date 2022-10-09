<p align="center">
  <h1 align="center">ghs</h2>
  <p align="center">Cross-platform CLI tool to generate your Github profile's stats and summary.<p>
  <p align="center">
    <a href="https://github.com/interviewstreet/ghs/blob/master/LICENSE">
      <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg" />
    </a>
    <a href="https://github.com/interviewstreet/ghs/pulls">
	    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="prs welcome">
    </a>
    <a href="https://github.com/interviewstreet/ghs">
    	<img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg" alt="platforms" />
    </a>
    <a href="https://pypi.org/project/ghs">
      <img src="https://img.shields.io/pypi/v/ghs.svg" />
    </a>
    <a href="https://pypi.org/project/ghs">
      <img src="https://img.shields.io/pypi/pyversions/ghs.svg" />
    </a>
    <a href="https://pypi.org/project/ghs">
      <img src="https://pepy.tech/badge/ghs" />
    </a>
    <a href="https://pypi.org/project/ghs">
      <img src="https://pepy.tech/badge/ghs/month" />
    </a>
  </p>
</p>

# Preview

<p align="center">
  <a href="https://asciinema.org/a/482833" target="_blank"><img src="https://asciinema.org/a/482833.svg" /></a>
</p>

Hop on to [examples](#examples) for other usecases.

---

Jump to:

- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using source code](#using-source-code)
  - [Docker](#docker)
- [Github PAT](#github-pat)
- [Usage](#usage)
- [Examples](#examples)
- [Installation Hiccups on Windows](#installation-hiccups-on-windows)
  - [Environment error](#could-not-install-package-due-to-environment-error)
  - [ghs command not found](#ghs-command-not-found-even-after-installing)
- [How to contribute?](#how-to-contribute)
- [Steps for pushing a new update](#steps-for-pushing-a-new-update)
- [Changelog](#changelog)
- [Privacy Notice](#privacy-notice)
- [License](#license)

## Installation

### Using pip

The stable version of this package is maintained on pypi, install using pip:

```bash
pip install ghs
```

### Using source code

This can be useful when you want to do a code contribution to this project. You can test and verify your local changes before submitting a Pull Request.

1. Clone the repository

```bash
git clone https://github.com/interviewstreet/ghs.git
```

2. Navigate to the project root and create a virtual environment

```bash
python -m venv venv
```

3. Activate the virtual environment
   - For macOS and linux, run `source venv/bin/activate`
   - For windows, run `.\venv\Scripts\activate`
4. Install the cli by running the following command while you are in the project root

```bash
pip install .
```

_Note_: You need to reinstall by running the pip command if you want the cli to pick up your code changes.

## Docker

```bash
docker build -t ghs:latest .
docker run -it ghs ghs --help
```

## Github PAT

Generate a Github personal access token (https://github.com/settings/tokens) and use the `ghs -t` command to save it in the config file. This will be used to make the API requests to Github. A happy side-effect of this is that your private contributions are also considered while generating the stats and the summary of your username.

Please make sure that you give the following scopes to the token:

- `repo`
- `read:user`
- `read:packages`

PS: Your Github PAT is not compromised by ghs. Please read the [Privacy Notice](#privacy-notice) to know more.

## Usage

```bash
ghs [options]
```

| Option                     | Description                                                                         |
| -------------------------- | ----------------------------------------------------------------------------------- |
| `-v` `--version`           | Print the cli version                                                               |
| `-t` `--token-update`      | Prompts the user for github PAT and saves it in the config file                     |
| `-u <username>`            | Print the general stats for the provided username                                   |
| `-s` `--summary`           | Print the summary of the user. The username should be provided using the `-u` flag. |
| `-c` `--copy-to-clipboard` | Copy the output to clipboard. Can be used with `-u` or `-s`.                        |
| `-h` `--help`              | Show the help message of the cli                                                    |

## Examples

### `ghs -u <username>`

Prints the general Github stats for the given username.

<p align="center">
  <a href="https://asciinema.org/a/482898" target="_blank"><img src="https://asciinema.org/a/482898.svg" /></a>
</p>

### copy to clipboard

Provide the `-c` flag to copy the output to your clipboard.

<p align="center">
  <a href="https://asciinema.org/a/482903" target="_blank"><img src="https://asciinema.org/a/482903.svg" /></a>
</p>

### Other options for summary

In addition to getting the Github summary from the beginning, you can also get the summary of the last 12 months or you can provide your own custom duration.

<p align="center">
  <a href="https://asciinema.org/a/482912" target="_blank"><img src="https://asciinema.org/a/482912.svg" /></a>
</p>

## Installation hiccups on windows

### Could not install package due to Environment Error

It can be solved by scoping the installation. Add the flag `--user` to the pip command (`pip install --user ghs`).

Alternatively, you can install the tool inside a virtual environment

### ghs command not found even after installing

Most likely the place where the command is installed is not in the system [PATH](<https://en.wikipedia.org/wiki/PATH_(variable)>). On windows, there are [a few places](https://stackoverflow.com/questions/25522743/where-does-pip-store-save-python-3-modules-packages-on-windows-8) where the packages might be installed. After confirming the location, [add that directory](https://www.computerhope.com/issues/ch000549.htm) to the PATH.

## How to contribute?

Please see [Contributing guidelines](https://github.com/interviewstreet/ghs/blob/master/CONTRIBUTING.md) for more information.

## Steps for pushing a new update

1. Bump the version in `ghs/__init__.py` (we follow semantic versioning).

2. Create an annotated tag for this commit with the version name `git tag -a v1.2.3 -m "v1.2.3"`. You can use this to publish a new release on the project's github page and the same can be used for maintaining the changelog.

3. Make sure you have [twine](https://pypi.org/project/twine/) and [build](https://pypi.org/project/build/) installed.

```
pip install build twine
```

3. Build the package

```
python -m build
```

This will create a source archive and a wheel inside the `dist` folder. You can inspect them to make sure that they contain the correct files.

4. Run twine sanity on the build files

```
twine check dist/*
```

5. First push the package on [TestPyPi](https://test.pypi.org/) so that you can test the updates without affecting the real PyPI index

```
twine upload -r testpypi dist/*

```

> Get the credentials for hackerrank dev PyPI account from karthik.

Twine will list the package url on TestPyPI. You can test and confirm your changes by installing the package.

6. Finally, run the following command to upload the package to PyPI

```
twine upload dist/*
```

> Get the credentials for hackerrank PyPI account from karthik.

7. Treat yourself with a scoop of tender coconut.

## Changelog

You can checkout [Releases](https://github.com/interviewstreet/ghs/releases) for the changelog.

## Privacy Notice

ghs does not collect any data.

- It has no home server. The Github PAT is stored locally in your machine.
- It doesn't embed any kind of analytic hooks in its code.

The only time ghs connects to a remote server is when you want to generate the stats and summary of your github profile. The cli uses the [Github GraphQL](https://docs.github.com/en/graphql) and [Github Rest](https://docs.github.com/en/rest) APIs to do so. The data collected via the APIs is not sent anywhere. It's displayed in your terminal or copied to your clipboard (only if you explicitly tell the tool to do so by providing the `-c` or `--copy-to-clipboard` flag).

## License

[MIT](https://github.com/interviewstreet/ghs/blob/master/LICENSE) © HackerRank

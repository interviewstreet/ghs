import pathlib

from setuptools import setup

import ghs

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()


setup(
    name="ghs",
    version=ghs.__version__,
    description="Get you Github profile's stats and summary.",
    packages=["ghs"],
    include_package_data=True,
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://github.com/interviewstreet/ghs",
    license="MIT",
    author="Hackerrank",
    author_email="pypi@hackerrank.com",
    keywords=["github", "cli", "utility", "command", "console"],
    install_requires=[
        "requests",
        "retry_requests",
        "python-dateutil",
        "termcolor",
        "colorama",
        "pyperclip",
        "halo",
    ],
    entry_points={"console_scripts": ["ghs=ghs.ghs:main_proxy"]},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)

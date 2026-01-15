import setuptools
from io import open

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slack_mr_bot",
    version="2.1.0",
    author="Chris Brookes",
    author_email="chris-brookes93@outlook.com",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "slack_mr_bot = gitlab_mr_bot.bot:run",
        ],
    },
    install_requires=[
        "slack_bolt==1.27.0",
        "python-gitlab==7.1.0",
    ]
)

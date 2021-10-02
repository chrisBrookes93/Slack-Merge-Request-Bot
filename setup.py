import setuptools
from io import open

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slack_mr_bot",
    version="0.1.0",
    author="Chris Brookes",
    author_email="chris-brookes93@outlook.com",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "slack_mr_bot = gitlab_mr_bot.bot:run",
        ],
    },
)

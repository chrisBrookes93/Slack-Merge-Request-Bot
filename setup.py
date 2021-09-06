import setuptools
from io import open

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='slack_mr_bot',
    version='0.0.1',
    author='Chris Brookes',
    author_email='chris-brookes93@outlook.com',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'slackclient==2.9.3',
        'slack_bolt==1.9.0',
        'python-gitlab==2.10.1'
    ],
)

from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='w3ai_sdk', # name of packe which will be package dir below project
    version='0.0.6',
    url='https://github.com/yourname/yourproject',
    author='AIOZ-AITeam',
    author_email='tu.chau.phan@aioz.io',
    description='W3AI Flatform API',
    long_description="Query data from W3AI flatform",
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['web3'],
)
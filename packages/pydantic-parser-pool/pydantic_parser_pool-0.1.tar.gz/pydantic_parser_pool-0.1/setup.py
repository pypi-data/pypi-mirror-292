from setuptools import setup, find_packages

setup(
    name='pydantic_parser_pool',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "langchain==0.2.14"
    ]
)
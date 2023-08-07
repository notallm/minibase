from setuptools import setup, find_packages

with open("requirements.txt") as handler:
    requirements = handler.readlines()

setup(
    name = "minibase",
    author = "Aarush Gupta",
    description = "a small base package for full-stack development with python",
    packages = find_packages(),
    install_requires = requirements
)

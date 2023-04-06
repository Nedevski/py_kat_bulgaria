"""Setup"""

from pathlib import Path
from setuptools import find_packages, setup

long_description = Path("README.md").read_text()

setup(
    name="kat_bulgaria",
    version="0.3.0",
    description="A library to check for existing obligations to KAT Bulgaria",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nedevski/py_kat_bulgaria",
    author="Nikola Nedevski",
    author_email="nikola.nedevski@gmail.com",
    license="MIT",
    packages=find_packages(include=["kat_bulgaria"]),
    install_requires=["httpx"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
)

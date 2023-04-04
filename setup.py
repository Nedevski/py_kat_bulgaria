"""Setup"""

from pathlib import Path
from setuptools import find_packages, setup

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text()

setup(
    name="kat_bulgaria",
    version="0.0.8",
    description="A library to check for existing obligations to KAT Bulgaria",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nedevski/py_kat_bulgaria",
    author="Nikola Nedevski",
    author_email="nikola.nedevski@gmail.com",
    license="MIT",
    packages=find_packages(include=["kat_bulgaria"]),
    install_requires=["urllib3"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
    package_data={"": ["*.pem", "**/*.pem", "*.crt", "**/*.crt", "*.cer", "**/*.cer"]},
)

"""Setup"""

from setuptools import find_packages, setup

setup(
    name="kat_bulgaria",
    version="0.0.7",
    description="A library to check for existing obligations to KAT Bulgaria",
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

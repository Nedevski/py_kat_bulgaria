from setuptools import find_packages, setup

setup(
    name="kat_bulgaria",
    version="0.0.1",
    description="A library to check for existing obligations to KAT Bulgaria",
    url="https://github.com/Nedevski/py_kat_bulgaria",
    author="Nikola Nedevski",
    author_email="nikola.nedevski@gmail.com",
    license="MIT",
    packages=find_packages(include=["kat_bulgaria"]),
    install_requires=["requests"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
)

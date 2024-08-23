from setuptools import find_packages, setup
import os
import subprocess


def read_readme():
    file_path = os.path.join(os.path.dirname(__file__), "README.md")
    with open(file_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    return readme_content


setup(
    name="cabysis-mail-man",
    version="1.0.3",  # Change this version using Mayor.Minor.Issue format before updating the master branch
    author="Cabysis",
    author_email="dev@cabysis.com",
    description="Cabysis email sender service",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'requests==2.32.3',
        'setuptools==73.0.1',
        'twine==5.1.1',
        'flake8==7.1.1',
        'pytest==8.3.2'],
    setup_requires=[],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
    license="MIT",
)


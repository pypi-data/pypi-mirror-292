"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-cluster-apicli",
    version="3.0.3",
    description="API client for Core API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://vcs.cyberfusion.nl/core/python3-cyberfusion-cluster-apicli",
    platforms=["linux"],
    packages=["cyberfusion.ClusterApiCli"],
    data_files=[],
    package_dir={"": "src"},
    install_requires=[
        "python3-cyberfusion-common~=2.0",
        "cached_property==1.5.2",
        "certifi==2022.9.24",
        "requests==2.28.1",
    ],
)

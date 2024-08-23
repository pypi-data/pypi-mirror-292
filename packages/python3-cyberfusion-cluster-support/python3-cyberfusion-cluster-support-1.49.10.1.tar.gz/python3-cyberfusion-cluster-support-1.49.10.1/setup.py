"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-cluster-support",
    version="1.49.10.1",
    description="API library for Core API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://vcs.cyberfusion.nl/core/python3-cyberfusion-cluster-support",
    platforms=["linux"],
    packages=[
        "cyberfusion.ClusterSupport",
        "cyberfusion.ClusterSupport.exceptions",
        "cyberfusion.ClusterSupport.tests_factories",
    ],
    package_dir={"": "src"},
    data_files=[],
    install_requires=[
        "python3-cyberfusion-common~=2.0",
        "python3-cyberfusion-cluster-apicli~=3.0",
        "cached_property==1.5.2",
        "factory_boy==2.11.1",
        "humanize==4.4.0",
        "rich==13.3.1",
    ],
)

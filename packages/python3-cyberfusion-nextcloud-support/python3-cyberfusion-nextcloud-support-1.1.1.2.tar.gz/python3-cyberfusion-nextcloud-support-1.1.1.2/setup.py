"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-nextcloud-support",
    version="1.1.1.2",
    description="Library for NextCloud.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-nextcloud-support",
    platforms=["linux"],
    packages=[
        "cyberfusion.NextCloudSupport",
    ],
    package_dir={"": "src"},
    data_files=[],
    install_requires=[
        "python3-cyberfusion-common~=2.10",
    ],
)

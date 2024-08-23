"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-external-providers-ip-ranges",
    version="2.1.1.2",
    description="Scripts to add IP ranges of external providers to ferm.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-external-providers-ip-ranges",
    platforms=["linux"],
    packages=[
        "cyberfusion.ExternalProvidersIPRanges",
    ],
    package_dir={"": "src"},
    data_files=[],
    entry_points={
        "console_scripts": [
            "external-providers-ip-ranges-cli=cyberfusion.ExternalProvidersIPRanges:main",
        ]
    },
    install_requires=[
        "requests==2.28.1",
        "python3-cyberfusion-common~=2.0",
        "python3-cyberfusion-ferm-support~=1.1",
    ],
)

"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-common",
    version="2.10.11.3.1",
    description="Common utilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-common",
    platforms=["linux"],
    packages=["cyberfusion.Common", "cyberfusion.Common.exceptions"],
    package_dir={"": "src"},
    data_files=[],
    install_requires=[
        "cached_property==1.5.2",
        "psutil==5.8.0",
        "requests==2.28.1",
    ],
)

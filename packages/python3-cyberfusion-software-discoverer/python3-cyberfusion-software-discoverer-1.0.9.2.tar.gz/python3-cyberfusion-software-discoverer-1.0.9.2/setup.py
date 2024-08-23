"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-software-discoverer",
    version="1.0.9.2",
    description="Library to discover software installed on system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-software-discoverer",
    platforms=["linux"],
    packages=["cyberfusion.SoftwareDiscoverer"],
    package_dir={"": "src"},
    data_files=[],
    install_requires=["PyYAML==6.0"],
)

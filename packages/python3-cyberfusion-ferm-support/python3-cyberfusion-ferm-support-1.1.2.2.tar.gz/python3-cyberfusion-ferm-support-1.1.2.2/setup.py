"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-ferm-support",
    version="1.1.2.2",
    description="Library for ferm.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-ferm-support",
    platforms=["linux"],
    packages=[
        "cyberfusion.FermSupport",
        "cyberfusion.FermSupport.configuration",
        "cyberfusion.FermSupport.exceptions",
    ],
    package_dir={"": "src"},
    data_files=[],
    install_requires=[
        "cached_property==1.5.2",
        "python3-cyberfusion-common~=2.0",
        "python3-cyberfusion-systemd-support~=1.0",
    ],
)

"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-queue-support",
    version="1.1.1.2",
    description="Library to queue actions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-queue-support",
    platforms=["linux"],
    packages=[
        "cyberfusion.QueueSupport",
        "cyberfusion.QueueSupport.items",
        "cyberfusion.QueueSupport.exceptions",
    ],
    package_dir={"": "src"},
    data_files=[],
    install_requires=[
        "python3-cyberfusion-systemd-support~=1.0",
    ],
)

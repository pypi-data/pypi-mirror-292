"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-aptly-apicli",
    version="1.0.2.2",
    description="API library for Aptly.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-aptly-apicli",
    platforms=["linux"],
    packages=["cyberfusion.AptlyApiCli"],
    package_dir={"": "src"},
    data_files=[],
    entry_points={
        "console_scripts": [
            "aptly-package-upload-add=cyberfusion.AptlyApiCli.package_upload_add:main",
        ]
    },
    install_requires=["certifi==2022.9.24", "requests==2.28.1"],
)

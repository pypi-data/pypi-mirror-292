import os
from setuptools import setup, find_packages

def get_version():
    version = os.environ.get('RELEASE_VERSION')
    if version is None:
        raise ValueError("RELEASE_VERSION environment variable is not set. Cannot proceed with package build.")
    return version

setup(
    name="openteleop",
    version=get_version(),  # Use the get_version function here
    packages=find_packages(),
    description="Python SDK for OpenTeleop",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/openteleop/openteleop-py",
    author="Devon Copeland",
    author_email="founders@serial.io",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=["requests"],
    include_package_data=True
)
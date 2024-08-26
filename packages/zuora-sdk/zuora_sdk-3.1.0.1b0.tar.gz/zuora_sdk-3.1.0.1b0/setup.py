# coding: utf-8

"""
    Zuora API Reference

    REST API reference for the Zuora Billing, Payments, and Central Platform! Check out the [REST API Overview](https://www.zuora.com/developer/api-references/api/overview/).  # noqa: E501

    OpenAPI spec version: 2024-05-20
    Contact: docs@zuora.com
"""
import sys

from setuptools import setup, find_packages
import os

NAME = "zuora_sdk"

VERSION = os.getenv('ZUORA_SDK_VERSION', '0.0.0')  # Default to '0.0.0' if the environment variable is not set

# Only raise an error if VERSION is not set during packaging (sdist or bdist_wheel)
if VERSION == '0.0.0' and any(cmd in sys.argv for cmd in ('sdist', 'bdist_wheel')):
    raise ValueError("Environment variable ZUORA_SDK_VERSION is not set!")

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil"]

setup(
    name=NAME,
    version=VERSION,
    description="Zuora API Reference",
    author="Zuora",
    url="",
    keywords=["Zuora", "SDK"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    long_description="""\
    REST API reference for the Zuora Billing, Payments, and Central Platform! Check out the [REST API Overview](https://www.zuora.com/developer/api-references/api/overview/).
    """
)

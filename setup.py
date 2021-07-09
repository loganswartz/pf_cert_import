#!/usr/bin/env python3
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pf_cert_import",
    version="1.0.0",
    author="Logan Swartzendruber",
    author_email="logan.swartzendruber@gmail.com",
    description="Automatically import certs into pfSense.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loganswartz/pf_cert_import",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
        pf_cert_import=pf_cert_import.cli:cli
    """,
)

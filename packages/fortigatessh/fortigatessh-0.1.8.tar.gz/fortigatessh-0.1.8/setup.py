#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2024 Nathan Liang

from setuptools import setup, find_packages

setup(
    name='fortigatessh',
    use_scm_version=True,
    setup_requires=['setuptools-scm'],
    author='Nathan Liang',
    description='A Python library for managing FortiGate devices via SSH',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=['fortigatessh'],
    install_requires=[
        'paramiko>=2.7.0',
        'paramiko-expect>=0.2.0',
    ],
    python_requires='>=3.6',
    license='Apache License 2.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Zzz(1309458652@qq.com)
# Description:

from setuptools import setup, find_packages

setup(
    name = 'biano',
    version = '0.2.2',
    keywords='biano',
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    description = "keyboard piano, just start",
    license = 'Apache License 2.0',
    url = 'https://github.com/buildCodeZ/biano',
    author = 'Zzz',
    author_email = '1309458652@qq.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = ['pynput>=1.7.6', 'numpy>=1.22.2', 'PyAudio>=0.2.12'],
)
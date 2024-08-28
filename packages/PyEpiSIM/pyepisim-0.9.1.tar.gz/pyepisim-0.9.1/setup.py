#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/26 10:37
# @Author  : 我的名字
# @File    : setup.py.py
# @Description : 这个函数是用来balabalabala自己写
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyEpiSIM",
    version="0.9.1",
    author="Anqi Xu",
    url='https://github.com/CDMBlab/PyEpiSIM',
    author_email="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={},
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    include_package_data=True,
    install_requires=[
        'numpy==1.22.4',
        'ttkbootstrap==1.10.1',
        'pandas==2.2.2',
        'sympy==1.13.2',
        'scipy==1.13.1',
        'openpyxl==3.1.5'
    ]
)

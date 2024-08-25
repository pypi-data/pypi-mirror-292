#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 0:50
# @Author  : pianshilengyubing
# @File    : sizhi3.py
# @Software: PyCharm
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
	name="sizhi",
	version="3.0.6",
	author="pianshilengyubing",
	author_email="1010221702@qq.com",
	description="中国行政区划四至点位获取、区划shp、geojson下载及流式裁剪链接",
	long_description=long_description,
	long_description_content_type="text/markdown",  # 所需要的依赖
	install_requires=[],  # 比如["flask>=0.10"]
	url="https://www.ykghs.top",
	packages=find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)

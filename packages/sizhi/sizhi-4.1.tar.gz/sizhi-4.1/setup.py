#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 0:50
# @Author  : pianshilengyubing
# @File    : sizhi3.py
# @Software: PyCharm
import setuptools
setuptools.setup(
	name="sizhi",
	version="4.1",
	author="pianshilengyubing",
	author_email="1010221702@qq.com",
	description="中国行政区划四至点位获取、区划shp、geojson下载及流式裁剪链接",
	long_description="此模块用来获取地图省市县乡镇四级行政区划的四至点位，默认左上右下，经度在前，纬度在后，请按该顺序编写代码。\n利用该模块，可以省去爬虫等工作时需要手动获取四至点位并转换坐标系的过程，便于节省代码，批量使用，还可使得代码更为可控。有获取行政区划的四至点位（包含全部区划的最小矩形即包络矩形）与自行输入俩种方式。3.0版本新增了下载行政区划shp、geojson文件，并可以返回url以方便利用gdal进行流式裁剪。",
	long_description_content_type="text/markdown",  # 所需要的依赖
	install_requires=[],  # 比如["flask>=0.10"]
	url="https://space.bilibili.com/31106656",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)

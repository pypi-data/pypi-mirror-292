# -*- coding: utf-8 -*-
# @Time : 2024/8/27 1:24
# @Author : DanYang
# @File : setup.py
# @Software : PyCharm
from setuptools import setup, find_packages

setup(
    name='XJTU-TGA',  # 替换为你的项目名称
    version='0.1.0',  # 你可以根据实际情况调整版本号
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.0',  # 你可以根据需要指定更具体的版本
        'plotly>=5.0.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'scipy>=1.7.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # 根据你的项目需求调整 Python 版本要求
    include_package_data=True,
    zip_safe=True,
)

# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = 'LinakDPGBt',
    version = '1.0.0',
    url = 'https://github.com/zewelor/linak_bt_desk.git',
    author = 'Michał Ciemięga',
    author_email = 'zewelor@gmail.com',
    description = 'Simple lib to control linak dpg remote over bluetooth',
    packages = find_packages(),
    install_requires = ['bluepy>=1.0.5','click'],
)

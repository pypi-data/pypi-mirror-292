#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 09:33:17 2023

@author: muthyala.7
"""

import setuptools


setuptools.setup(
    name="TorchSisso",
    version="0.1.2",
    author="Madhav Muthyala",
    author_email="madhavreddymuthyala@gmail.com",
    description="",
    url="https://github.com/PaulsonLab/TorchSISSO",
    packages=setuptools.find_packages(),
    install_requires=[
        "torch",
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

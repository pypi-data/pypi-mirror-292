# setup.py
import io
import os
from setuptools import setup, find_packages
# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))
# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = DESCRIPTION
# Package meta-data.
NAME = 'STCC'
DESCRIPTION = 'consensus clustering enhances spatial domain detection for spatial transcriptomics data.'
EMAIL = '2578073006@qq.com'
URL="https://github.com/hucongcong97/STCC"
AUTHOR = 'congconghu'
VERSION = '1.0.3'
setup(
name=NAME,
version=VERSION,
author=AUTHOR,
author_email=EMAIL,
 license='MIT',
description=DESCRIPTION,
 url=URL,
long_description_content_type="text/markdown",
long_description=long_description,
packages=find_packages(),
 install_requires=["numpy","pandas", "scikit_learn", "cvxopt", 
                   "scipy", "seaborn"],
 classifiers=[
 'Programming Language :: Python',
 "Programming Language :: Python :: 3",
 "License :: OSI Approved :: MIT License",
 "Operating System :: OS Independent",
 ],
)

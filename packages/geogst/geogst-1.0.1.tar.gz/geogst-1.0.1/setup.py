#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith('#')]


setup(
    name='geogst',
    version='1.0.1',
    author="Mauro Alberti",
    author_email="alberti.m65@gmail.com",
    description="geogst is a structural geology module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/mauroalberti/geogst",
    project_urls={
        "Bug Tracker": "https://gitlab.com/mauroalberti/geogst/-/issues",
        "Documentation": "https://gitlab.com/mauroalberti/geogst/-/blob/main/README.md",
        "Source Code": "https://gitlab.com/mauroalberti/geogst/-/tree/main",
    },
    packages=find_packages(exclude=("tests",)),
    install_requires=parse_requirements("requirements.txt"),
    license="MIT",
    classifiers=[
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3 :: Only",
                   "Topic :: Software Development",
                   "Topic :: Scientific/Engineering :: GIS",
                   "Topic :: Utilities"
               ],
    python_requires='>=3',
    tests_require=['pytest'],
)

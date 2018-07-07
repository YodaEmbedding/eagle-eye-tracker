#!/usr/bin/env python3
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "eagleeyetracker",
    version = "0.0.1",
    author = "Mateen Ulhaq",
    description = "Eagle Eye Tracker",
    license = "MIT",
    keywords = "deeplearning tracking",
    packages=['simulation', 'test', 'doc'],
    long_description=read('README.md'),
    install_requires=[
        'numpy-quaternion',
        'numpy_ringbuffer',
    ],
)

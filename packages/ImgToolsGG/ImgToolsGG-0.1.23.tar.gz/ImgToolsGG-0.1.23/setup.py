# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="ImgToolsGG",  # todo fix this name
    version="0.1.23",
    description="test how to make a package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/buxuele/ImgToolsGG",
    author="MeJustAFanOfGSW",
    author_email="fanchuangwater@gmail.com", # todo fix this
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent"
    ],
    packages=["src"],  # todo: main folder
    include_package_data=True,
    install_requires=["numpy"]
)



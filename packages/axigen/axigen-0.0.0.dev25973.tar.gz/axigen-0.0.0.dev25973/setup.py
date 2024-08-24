import sys
from setuptools import setup, find_namespace_packages

version = sys.argv[1]
del sys.argv[1]

setup(
    name="axigen",
    version=version,
    author="Axigen Messaging",
    author_email="info@axigen.com",
    description="Python library for automating Axigen administration tasks",
    packages=find_namespace_packages(include=['axigen.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


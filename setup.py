import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="roadrunner",
    version="0.1",
    author="Felipe Reyes",
    author_email="felipe.reyes@canonical.com",
    description="A runner for juju blender",
    license="Apache License v2",
    keywords="juju testing",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ],
    entry_points={
        'console_scripts': [
            'roadrunner = roadrunner.cli:main',
        ]
    }
)

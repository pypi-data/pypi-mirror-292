from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hs3",
    version="1.0.2",
    description="Utilities for the HS3 standard in high-energy physics",
    author="Carsten Burgard",
    author_email="cburgard@cern.ch",
    url="https://github.com/hep-statistics-serialization-standard/python-hep-statistics-serialization-standard/tree/master",
    packages=find_packages(include=["hs3", "hs3.*"]),
    long_description=long_description,  
    long_description_content_type="text/markdown", 
    scripts=["bin/hs3diff", "bin/hs3tographml"],
    install_requires=[
        # List any third-party dependencies here, for example:
        # "numpy>=1.19.2",
    ],
    license="BSD-3-Clause",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

"""
@author: Nusab Taha
@contact: https://nusab19.pages.dev/
@license: MIT License, see LICENSE file

Copyright (C) 2023 - 2024
"""


from setuptools import setup

version = "3.3"


with open("README.md", "r", encoding="utf8") as f:
    long_description = f.read()
with open("requirements.txt", "r", encoding="utf8") as f:
    requirements = f.read().split()

setup(
    name="nusuGraph",
    version=version,
    author="Nusab Taha",
    author_email="nusabtaha33@gmail.com",
    url="https://github.com/Nusab19/nusuGraph",
    description="An asynchronous and simplified Telegraph API Wrapper in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url=f"https://github.com/Nusab19/nusuGraph/archive/v{version}.zip",
    license="MIT",
    packages=["nusugraph"],
    install_requires=requirements,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

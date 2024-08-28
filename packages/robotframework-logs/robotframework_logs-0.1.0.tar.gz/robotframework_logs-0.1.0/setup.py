from setuptools import setup, find_packages

setup(
    name="robotframework-logs",
    version="0.1.0",
    author="Mikko Korpela",
    author_email="mikko.korpela@gmail.com",
    description="A client package for handling Robot Framework logs",
    long_description="A comprehensive client tool for viewing, analyzing, and managing Robot Framework logs, designed to work with the robotframework-logs.com cloud service.",
    long_description_content_type="text/markdown",
    url="https://github.com/mkorpela/robotframework-logs",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

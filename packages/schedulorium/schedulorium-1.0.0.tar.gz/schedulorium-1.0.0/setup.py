from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    description = f.read()

setup(
    name = "schedulorium",
    version = "1.0.0",
    author = "Roberto Schinina",
    author_email = "roberto.schinina02@gmail.com",
    description="A small package to create a timetable using integer programming",
    packages = find_packages(),
    long_description = description,
    long_description_content_type = "text/markdown",
    install_requires = [
        "numpy",
        "pandas",
        "matplotlib",
        "amplpy",
        "openpyxl"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
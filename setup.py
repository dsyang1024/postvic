from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="postvic", 
    version="0.3.0",
    author = 'DK Yang',
    author_email = 'yang2309@purdue.edu',
    url='https://github.com/dsyang1024/postvic.git',
    description="Analysis tools for VIC simulation outputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPL-3.0-only",
    packages=find_packages()
)
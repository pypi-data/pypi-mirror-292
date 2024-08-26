from setuptools import setup, find_packages

VERSION = "0.0.4"
DESCRIPTION = "A Collection of Simple Data Structures"
LONG_DESCRIPTION = "A Collection of Simple Data Structures"

setup(
    name="simplepyds",
    version=VERSION,
    author="Theophilus Nenhanga",
    author_email="theonenhanga@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["typing"],
    keywords=["data structures"],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)

from setuptools import setup

import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
path_to_readme = os.path.join(here, "README.md")

long_description = """# Mocker db

MockerDB

A python module that contains mock vector database like solution built around
dictionary data type. It contains methods necessary to interact with this 'database',
embed, search and persist.

"""

if os.path.exists(path_to_readme):
  with codecs.open(path_to_readme, encoding="utf-8") as fh:
      long_description += fh.read()

setup(
    name="mocker_db",
    packages=["mocker_db"],
    install_requires=['### mocker_db.py', 'pyyaml', 'hnswlib==0.8.0', 'attrs>=22.2.0', 'requests', 'sentence-transformers==2.2.2', 'click==8.1.3', 'uvicorn==0.29.0', 'gitpython==3.1.41', 'appdirs==1.4.3', 'fastapi==0.109.1', 'gridlooper==0.0.1', 'httpx', 'dill==0.3.7', 'numpy==1.26.0'],
    classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Intended Audience :: Science/Research', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.9', 'Programming Language :: Python :: 3.10', 'Programming Language :: Python :: 3.11', 'License :: OSI Approved :: MIT License', 'Topic :: Scientific/Engineering'],
    long_description=long_description,
    long_description_content_type='text/markdown',

    entry_points = {'console_scripts': ['mockerdb = mocker_db.cli:cli']},

    author="Kyrylo Mordan", author_email="parachute.repo@gmail.com", description="A mock handler for simulating a vector database.", version="0.2.2"
)

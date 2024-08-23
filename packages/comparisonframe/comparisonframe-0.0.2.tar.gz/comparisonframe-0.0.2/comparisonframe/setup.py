from setuptools import setup

import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
path_to_readme = os.path.join(here, "README.md")

long_description = """# Comparisonframe

Comparison Frame is designed to automate and streamline the process of comparing textual data, particularly focusing on various metrics
such as character and word count, punctuation usage, and semantic similarity.
It's particularly useful for scenarios where consistent text analysis is required,
such as evaluating the performance of natural language processing models, monitoring content quality,
or tracking changes in textual data over time using manual evaluation.

"""

if os.path.exists(path_to_readme):
  with codecs.open(path_to_readme, encoding="utf-8") as fh:
      long_description += fh.read()

setup(
    name="comparisonframe",
    packages=["comparisonframe"],
    install_requires=['### comparisonframe.py', 'pandas==2.1.1', 'mocker_db==0.2.1', 'numpy==1.26.0', 'attrs>=23.2.0'],
    classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Intended Audience :: Science/Research', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.9', 'Programming Language :: Python :: 3.10', 'Programming Language :: Python :: 3.11', 'License :: OSI Approved :: MIT License', 'Topic :: Scientific/Engineering'],
    long_description=long_description,
    long_description_content_type='text/markdown',

    author="Kyrylo Mordan", author_email="parachute.repo@gmail.com", description="A simple tool to compare textual data against validation sets.", version="0.0.2"
)

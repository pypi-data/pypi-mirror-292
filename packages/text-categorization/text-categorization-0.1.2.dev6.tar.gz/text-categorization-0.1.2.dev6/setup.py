# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper for importing package."""

import pathlib

import setuptools

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()


setuptools.setup(
  name='text-categorization',
  version='0.1.2.dev6',
  python_requires='>3.10',
  description='Library for performing trends analysis via LLMs.',
  long_description=README,
  long_description_content_type='text/markdown',
  author='Google Inc. (gTech gPS CSE team)',
  author_email='no-reply@google.com',
  license='Apache 2.0',
  classifiers=[
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.11',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
  ],
  packages=setuptools.find_packages(),
  package_data={'': ['*.txt']},
  install_requires=[
    'fastapi==0.111.0',
    'smart_open',
    'google-ads-api-report-fetcher[bq]==1.14.3',
    'langchain==0.2.7',
    'langchain_chroma==0.1.2',
    'langchain-core==0.2.21',
    'langchain-community==0.2.7',
    'langchain-google-genai==1.0.7',
    'chromadb==0.5.5 ',
    'db-dtypes==1.2.0',
  ],
  setup_requires=['pytest-runner'],
  tests_requires=['pytest', 'pytest-mock', 'pandas'],
  entry_points={
    'console_scripts': [
      'text-categorizer=entrypoints.cli:main',
    ]
  },
)

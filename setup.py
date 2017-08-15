#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Setup script."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa. Ipa provides an api and command line
# utilities for testing images in the Public Cloud.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import find_packages, setup

with open('README.asciidoc') as readme_file:
    readme = readme_file.read()

requirements = [
    'azurectl>=3.0.1',
    'boto3',
    'Click',
    'paramiko',
    'pytest',
    'PyYAML',
    'testinfra',
]

test_requirements = [
    'coverage',
    'flake8',
    'pytest-cov',
    'vcrpy'
]

tox_requirements = [
    'tox',
    'tox-pyenv'
]

dev_requirements = [
    'bumpversion',
    'pip>=7.0.0',
] + test_requirements


setup(
    name='ipa',
    version='0.0.1',
    description="Package for automated testing of cloud images.",
    long_description=readme,
    author="SUSE",
    author_email='public-cloud-dev@susecloud.net',
    url='https://github.com/SUSE/pubcloud/ipa',
    packages=find_packages(),
    package_dir={'ipa':
                 'ipa'},
    entry_points={
        'console_scripts': [
            'ipa=ipa.scripts.cli:main'
        ]
    },
    include_package_data=True,
    python_requires='>=3.4',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'test': test_requirements,
        'tox': tox_requirements
    },
    license='GPLv3+',
    zip_safe=False,
    keywords='ipa',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

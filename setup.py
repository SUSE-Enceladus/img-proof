#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

from setuptools import find_packages, setup

with open('README.asciidoc') as readme_file:
    readme = readme_file.read()

requirements = [
    'boto3',
    'Click',
    'ec2utilsbase',
]

dev_requirements = [
    'bumpversion',
    'flake8',
    'pip>=7.0.0',
]

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
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements
    },
    license="MIT license",
    zip_safe=False,
    keywords='ipa',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)

# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'rb') as stream:
    readme = stream.read().decode('utf8')

setup(
    long_description=readme,
    name='flake8-todos',
    version='0.1.4',
    description='Check TODOs in the project',
    project_urls={'repository': 'https://github.com/orsinium-labs/flake8-todos'},
    author='Gram <gram@orsinium.dev>',
    license='MIT',
    keywords='flake8 flake8-plugin linter styleguide code quality',
    classifiers=[
        'Development Status :: 4 - Beta', 'Environment :: Console',
        'Framework :: Flake8', 'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: BSD License'
    ],
    entry_points={
        'flake8.extension': ['T00 = flake8_todos:Checker'],
    },
    packages=['flake8_todos'],
    package_data={},
    install_requires=[
        'flake8',
        'pycodestyle',
    ],
    extras_require={
        'dev': [
            'isort[pyproject]',
            'pytest',
        ],
    },
)

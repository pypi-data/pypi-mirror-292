#!/usr/bin/env python3
from setuptools import setup

from src.midpoint_cli import __version__


def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


def parse_requirements(filename):
    """ Load requirements from a requirements file """
    with open(filename, 'r') as f:
        return [line.strip() for line in f
                if not line.startswith('#')]


setup(
    name='midpoint-cli',
    version=__version__,
    packages=['midpoint_cli', 'midpoint_cli.client', 'midpoint_cli.prompt'],
    package_dir={'midpoint_cli': 'src/midpoint_cli',
                 'midpoint_cli.client': 'src/midpoint_cli/client',
                 'midpoint_cli.prompt': 'src/midpoint_cli/prompt'
                 },
    scripts=['src/midpoint-cli'],
    test_suite='test',
    setup_requires=['pytest-runner'],
    install_requires=parse_requirements('requirements.txt'),
    tests_require=['pytest'],
    url='https://gitlab.com/alcibiade/midpoint-cli',
    license='MIT',
    author='Yannick Kirschhoffer',
    author_email='alcibiade@alcibiade.org',
    description='A command line client to Midpoint Identity Management system.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)

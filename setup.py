#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = \
    ['requests>=2.24.0',
     'websockets>=8.1',
     'wheel>=0.35.1'
     ]

setup(
    name='signalr-client-aio',
    version='0.0.2.8.2',
    author='Mikhail Solovev',
    author_email='mike@solovjov.net',
    license='MIT',
    url='https://github.com/r3bers/python-signalr-client',
    packages=find_packages(exclude=['tests*']),
    install_requires=install_requires,
    description='Simple python SignalR client using asyncio.',
    download_url='https://github.com/r3bers/python-signalr-client.git',
    keywords=['signalr', 'sginalr-weboscket', 'signalr-client', 'signalr-asyncio', 'signalr-aio'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7'
    ]
)

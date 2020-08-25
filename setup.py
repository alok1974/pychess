# -*- coding: utf-8 -*-
from distutils.core import setup
from glob import glob


PACKAGE_NAME = 'pychess'
PACKAGE_VERSION = '0.1'


setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='The game of Chess in python',
    author='Alok Gandhi',
    author_email='alok.gandhi2002@gmail.com',
    url='https://github.com/alok1974/pychess',
    packages=[
        'pychess',
        'pychess.resources',
    ],
    package_data={
        'pychess': ['resources/*/*.*'],
    },
    package_dir={
        'pychess': 'src/pychess'
    },
    scripts=glob('src/scripts/*'),
    install_requires=[
        'Pillow >=7.2.0'
        'svglib >=1.0.0'
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language:: Python:: 3.7',
        'Topic :: Games/Entertainment :: Board Games',
    ],
)

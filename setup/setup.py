from setuptools import setup, find_packages

setup(
    name='yourpackage',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'python3-PyQt5',
        'python3-matplotlib',
        'python3-numpy',
        'python3-pandas',
    ],
)
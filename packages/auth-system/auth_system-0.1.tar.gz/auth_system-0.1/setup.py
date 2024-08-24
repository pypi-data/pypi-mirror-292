# auth_system/setup.py

from setuptools import setup, find_packages

setup(
    name='auth_system',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Django>=3.0,<5.0',
        'djangorestframework>=3.12,<4.0',
    ],
)

"""
Setup file for auth_utils package
"""
from setuptools import setup, find_packages

setup(
    name='auth_vpetrov',
    version='0.4.8',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'pydantic',
        'user-vpetrov',
        'typing',
        'requests',
    ],
)

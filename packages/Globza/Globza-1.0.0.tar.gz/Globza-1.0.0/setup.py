# setup.py

from setuptools import setup, find_packages

setup(
    name='Globza',
    version='1.0.0',
    license='Proprietary',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Sergei Sychev',
    author_email='sch@triz-ri.com',
    description='Python library to interact with the universal api service',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
from setuptools import setup, find_packages

setup(
    name='yanivtils',
    version='0.2.0',
    author='Yaniv',
    author_email='yanivdorgalron@gmail.com',
    description='A collection of useful utilities for Python developers',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


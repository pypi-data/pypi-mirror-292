# setup.py

from setuptools import setup, find_packages

setup(
    name='llamaverify',
    version='0.1.6',
    description='A package for dehallucinating LLM outputs.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'huggingface_hub','requests'  # or whatever libraries you're using
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

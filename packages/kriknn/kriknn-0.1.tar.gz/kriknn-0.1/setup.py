from setuptools import setup, find_packages
from pathlib import Path

dir = Path(__file__).parent
with open(dir / 'README.md', encoding='utf-8') as f:
  long_description = f.read()

setup(
    name='kriknn',
    version='0.1',
    description='KrikNN is a library that includes various components for neural network operations and tensor manipulations. This README provides an overview of the `Tensor` class and its functionality, as well as instructions for running the tests.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Andrew Krikorian',
    license='MIT',
    url='https://github.com/andykr1k/kriknn',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    project_urls={
        'Bug Reports': 'https://github.com/andykr1k/kriknn/issues',
        'Source': 'https://github.com/andykr1k/kriknn',
    },
    include_package_data=True)

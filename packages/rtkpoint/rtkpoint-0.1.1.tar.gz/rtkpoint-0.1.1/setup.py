from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='rtkpoint',
    version='0.1.1',
    description='A Python library for interacting with RTKPOINT, a NTRIP caster',
    author='Rika Inc.',
    author_email='developer@rtkpoint.com',
    packages=find_packages(),
    install_requires=[
        'pyrtcm',  # Ensure to list all the required packages
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
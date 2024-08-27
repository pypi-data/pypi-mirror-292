from setuptools import setup, find_packages

from pathlib import Path

# Read the contents of README.md

this_directory = Path(__file__).parent
long_description = (this_directory/"README.md").read_text()

setup(
    name='argument_mining_framework',
    version='0.0.3',
    description='Argument Mining Framework (AMF) is a comprehensive toolkit designed to streamline and unify various argument mining modules into a single platform.',
    readme = "README.md",
    author='Debela',
    author_email='d.t.z.gemechu@dundee.ac.uk',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'transformers',
        'torch',
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)


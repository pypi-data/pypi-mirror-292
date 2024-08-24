from setuptools import setup, find_packages

setup(
    name='wirehead',
    version='0.9.0',
    packages=find_packages(),
    install_requires=[
        'pymongo',
        'torch',
        'numpy',
        'PyYaml',
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)

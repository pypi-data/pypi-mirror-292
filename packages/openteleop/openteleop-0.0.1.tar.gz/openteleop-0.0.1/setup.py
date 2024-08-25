from setuptools import setup, find_packages

setup(
    name='openteleop',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'openteleop=openteleop.main:main',
        ],
    },
)

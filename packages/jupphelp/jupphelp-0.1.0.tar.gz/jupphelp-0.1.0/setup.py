from setuptools import setup, find_packages

setup(
    name='jupphelp',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests', 
    ],
    entry_points={
        'console_scripts': [
            'jupphelp=jupphelp.helper:init_helper',
        ],
    },
)

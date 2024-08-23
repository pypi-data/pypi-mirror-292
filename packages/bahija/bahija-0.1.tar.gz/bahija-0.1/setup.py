from setuptools import setup, find_packages

setup(
    name="bahija",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bahija=bahija.main:print_ena_behija',
        ],
    },
)

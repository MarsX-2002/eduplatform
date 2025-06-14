from setuptools import setup, find_packages

setup(
    name="eduplatform",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "PyJWT>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'eduplatform=eduplatform.cli.main:main',
        ],
    },
)

from setuptools import setup, find_packages

setup(
   name='102103417_topsis_ojaswani',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'topsis=topsis:main',  
        ],
    },
)
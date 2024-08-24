from setuptools import setup, find_packages

setup(
    name="pysics_lab",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=2.0.1",
        "scipy>=1.13.0",
        "matplotlib>=3.8.4",
        "tabulate>=0.9.0"
    ]
)
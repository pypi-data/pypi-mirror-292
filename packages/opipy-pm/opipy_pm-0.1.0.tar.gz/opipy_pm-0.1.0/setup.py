from setuptools import setup, find_packages

setup(
    name="opipy_pm",
    version="0.1.0",
    author="Daniel E. Diaz Almeida",
    author_email="daniel.diazalmeida@opi-solutions.com",
    description="OPI Solutions Python package for Predictive Maintenance",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/OPISolutions/opipy_pm",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
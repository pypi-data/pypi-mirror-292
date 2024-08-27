from setuptools import setup, find_packages

setup(
    name="wedgie",
    version="0.0.5.13",
    author="Chad Roberts",
    author_email="jcbroberts@gmail.com",
    description="A public Python package for miscellaneous reusable functionality",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/deathbywedgie/wedgie-py",
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires='>=3.7',
    install_requires=[
        "structlog",
        "tinydb >= 4.8.0",
        "tabulate >= 0.9.0",
    ],
)

import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = os.getenv("VERSION")

setuptools.setup(
    name="powercicd",
    version=version,
    author="jeromerg",
    author_email="jeromerg@gmx.net",
    description="Utility to automate the CI/CD process for Power Platform projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeromerg/powercicd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "aiohttp",
        "azure-identity",
        "coverage",
        #"ipykernel",
        "jsonpath-ng",
        "nest_asyncio",
        "pydantic",
        #"pytest",
        "pyyaml",
        "requests",
        "selenium",
        "tabulate",
        "tenacity",
        "typer[all]",
    ],
    entry_points={
        'console_scripts': [
            'powercicd=powercicd.cli:main_cli',
        ],
    },
    python_requires='>=3.10',
)
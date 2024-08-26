import pathlib
import setuptools

# Read the contents of the README file
long_description = pathlib.Path("README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="pyworldatlas",
    version="0.0.10",
    description="Comprehensive and Lightweight Country Data Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://jcari-dev.github.io/pyworldatlas-documentation/",
    author="jcari-dev",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="country data atlas global statistics geography government economy",
    python_requires=">=3.8, <3.13",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "pyworldatlas": ["data/*.sqlite3"],
    },
    entry_points={
        "console_scripts": [
            "pyworldatlas=pyworldatlas.cli:main",
        ],
    },
    project_urls={
        "Documentation": "https://jcari-dev.github.io/pyworldatlas-documentation/",
        "Issue Tracker": "https://github.com/jcari-dev/pyworldatlas-issue-tracker",
        "PyPI": "https://pypi.org/project/pyworldatlas/",
    },
)

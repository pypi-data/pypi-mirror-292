import pathlib
import setuptools

setuptools.setup(
    name="pyworldatlas",
    version="0.0.7",
    description="Brief description.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://www.example.com",
    author="jcari-dev",
    license="The Unlicense",
    entry_points={
        "console_scripts": [
            "pyworldatlas=pyworldatlas.cli:main",
        ],
    },
    project_urls={
        "Documentation": "https://www.example.com/docs",
        "Source": "https://www.example.com/source",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8, <3.13",
    packages=setuptools.find_packages(),
    include_package_data=True,
)

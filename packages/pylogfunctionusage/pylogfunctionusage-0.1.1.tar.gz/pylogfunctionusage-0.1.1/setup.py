from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="pylogfunctionusage",  # Required
    version="0.1.0",  # Required

    description="LogFunctionUsage in pylogfunctionusage is a Python decorator designed to enhance the logging capabilities of your functions by wrapping them in a try: block. It logs function usage, including calls, exceptions, and results, to an SQLite table",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/USERNAME/pylogfunctionusage",  # Optional
    # This should be your name or the name of the organization which owns the
    # project.
    author="Ambroise Dobosz",  # Optional
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",

    ],

    keywords="logging, monitoring, sql, sqlite, pylogfunctionusage, LogFunctionUsage",  # Optional
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required

    python_requires=">=3.6, <4",

    # List additional URLs that are relevant to your project as a dict.
    project_urls={  # Optional
        "Bug Reports": "https://github.com/USERNAME/pylogfunctionusage/issues",
        "Source": "https://github.com/USERNAME/pylogfunctionusage",
    },
)
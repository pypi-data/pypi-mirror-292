from pathlib import Path
from setuptools import find_packages, setup

setup(
    name = "airtable_pack",
    version = "0.0.8",
    author = "Andrea Soledad Guerra",
    packages = find_packages(),
    description = "Python wrapper for Airtable Pack.",
    long_description = Path("README.md").read_text(),
    long_description_content_type = "text/markdown",
    url = "https://pypi.org/project/airtable_pack/",
    project_urls = {
        "Source": "https://github.com/AlejoPrietoDavalos/airtable_pack/"
    },
    python_requires = ">=3.11",
    install_requires = [
        "pyairtable>=2.3.3"
    ],
    include_package_data = True
)

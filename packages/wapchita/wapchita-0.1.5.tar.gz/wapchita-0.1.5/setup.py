from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="wapchita",
    version="0.1.5",
    author="Alejo Prieto Dávalos",
    author_email="alejoprietodavalos@gmail.com",
    packages=find_packages(),
    description="Python SDK para la API de Wapchita https://wapchita.com/.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/wapchita/",
    project_urls={
        "Source": "https://github.com/AlejoPrietoDavalos/wapchita/"
    },
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.32",
        "pydantic>=2.8",
        "tenacity>=8.4.0",
        "httpx>=0.27.0"
    ],
    include_package_data=True
)

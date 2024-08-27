from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_ishibashi",
    version="0.1",
    author="TheoShiba",
    author_email="theoshiba2005@gmail.com",
    description="Image Processing Package",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheoIshibashi/image-processing-package",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.6",
)
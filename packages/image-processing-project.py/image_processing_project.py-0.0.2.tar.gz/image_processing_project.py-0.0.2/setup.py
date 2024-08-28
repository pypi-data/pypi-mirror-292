from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_project.py",
    version="0.0.2",
    author="Yuri M.",
    author_email="yurimacenadev@gmail.com",
    description="Image processing project in Python",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yurimacena/image-processing-project.py",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8"
)
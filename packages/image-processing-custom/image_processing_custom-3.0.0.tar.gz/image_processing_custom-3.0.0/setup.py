from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_custom",
    version="3.0.0",
    author="João Paulo",
    author_email="ojpojao@gmail.com",
    description="Pacote de processamento de imagens usando o skimage",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ojpojao/image-processing-custom",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
)

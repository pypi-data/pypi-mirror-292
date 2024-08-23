from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processingv777",
    version="0.0.2",
    author="Claudio_nogueira",
    author_email="claudio.nogueira888@hotmail.com",
    description="Processamento de imagens",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/5qU4llV777/Processamento-de-Imagens-com-Python",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.12',
)
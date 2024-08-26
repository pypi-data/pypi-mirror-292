from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

setup(
    name='conversor_andre_conforti',
    version='0.0.1',
    author='Andre Conforti',
    author_email='andre.r.m.conforti@gmail.com',
    description='Pacote simples para conversao de unidades.',
    long_description=page_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
)
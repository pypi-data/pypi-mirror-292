from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="attributes_serializer",
    version="1.0.1",
    author="derijabyla",
    author_email="dulugov@gmail.com",
    description="Module to interact with marketplaces",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
)

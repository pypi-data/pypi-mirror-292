from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="group2p",
    version="0.2.0",
    packages=find_packages(),
    requires=[
        "requests"
        ],
    long_description=description,
    long_description_content_type="text/markdown"
)
from setuptools import setup, find_packages

setup(
    name="NumPlateVision", 
    version="0.1.0",
    author="Elliott Cooper",
    author_email="elliottcoops@gmail.com",
    description="Extracting a number plate from an image and recognising the characters on them",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/elliottcoops/Number-Plate-Recognition",
    packages=find_packages(),
    python_requires='>=3.11'
)
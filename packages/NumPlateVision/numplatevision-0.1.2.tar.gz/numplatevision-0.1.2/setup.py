from setuptools import setup, find_packages

setup(
    name="NumPlateVision", 
    version="0.1.2",
    author="Elliott Cooper",
    author_email="elliottcoops@gmail.com",
    description="Extracting a number plate from an image and recognising the characters on them",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/elliottcoops/Number-Plate-Recognition",
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[
        "numpy>=1.26.4",
        "keras==3.5.0",
        "opencv-python>=4.10.0.84",
        "tensorflow>=2.17.0",
        "torch>=2.4.0",
        "pillow>=10.4.0",
        "transformers>=4.44.0"
    ],
    package_data={
        'NumPlateVision': ['model/*.h5']
    },
    include_package_data=True,       
)
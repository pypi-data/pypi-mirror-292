from setuptools import setup, find_packages

setup(
    name="periorbital_package",
    version="0.1.0",
    description="A package for periorbital distance segmentation and measurement.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Georgie Nahass",
    author_email="gnahas2@uic.edu",
    url="https://github.com/monkeygobah/periorbital_package",  
    packages=find_packages(include=["periorbital"]),
    install_requires=[
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "huggingface_hub",
        "numpy>=1.19.2",
        "scipy>=1.5.2",
        "matplotlib>=3.3.2",
        "opencv-python>=4.5.1",
        "scikit-learn>=0.24.2",
        "pillow>=8.0.1",
        "pandas>=1.1.3",
        "mediapipe>=0.8.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

from setuptools import setup, find_packages


setup(
    name="DataProFileExt",  # Your package name
    version="0.1.2",  # Initial version
    author="Justin Degrechie",  # Your name
    author_email="justin.doodle3845@gmail.com",  # Your email
    description="A package for .DataPro file extensions. .DataPro is like json but worse, however its really easy to use.",
    long_description=open("README.md").read(),  # Read the long description from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/BlueScriptsAndDies/DataPro-File-Extension",  # Your project repository URL
    packages=find_packages(),  # Automatically find all packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Change if using a different license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
    install_requires=[],  # List dependencies here if any
)

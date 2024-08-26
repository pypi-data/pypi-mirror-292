# setup.py

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="hello-sid",  # Your package name
    use_scm_version=True,  # Use setuptools-scm to handle versioning
    setup_requires=["setuptools>=42", "setuptools-scm"],  # Use attr to get the version from your package
    description="A package for saying hello.",
    author="Siddharth Choudhury",
    author_email="skchoudhury126@gmail.com",
    packages=find_packages(where="."),  # Specifies that packages are in the root directory
    package_dir={"": "."},  # Root directory is the package directory
    long_description=long_description,
    long_description_content_type="text/markdown",  # or "text/x-rst" if using reStructuredText
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)

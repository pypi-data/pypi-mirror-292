from setuptools import setup, find_packages

setup(
    name="import_from_gist",
    version="0.1.0",
    description="A Python library to import modules from GitHub Gists.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/OhadRubin/import_from_gist",
    author="Ohad Rubin",
    author_email="iohadrubin@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

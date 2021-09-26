"""Happy Net CLI Package Setup"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="happynet",
    version="0.0.1",
    author="Sean Slater",
    author_email="seanslater@whatno.io",
    description="A command line tool for interacting with Happy Net Box",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spslater/happynetpy",
    license="MIT License",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    keywords="finger",
    python_requires=">=3.9",
)

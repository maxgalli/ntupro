import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ntupro-magalli", # Replace with your own username
    version="0.0.0",
    author="Massimiliano Galli",
    author_email="massimiliano.galli.95@gmail.com",
    description="Innovative package to optimize HEP analyses based on ROOT RDataFrame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maxgalli/ntupro",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

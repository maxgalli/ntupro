import setuptools

readme = open("README.md", "r")
long_description = ''
for line in readme:
    if not line.startswith('<img'):
        long_description += line

setuptools.setup(
    name="ntupro",
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

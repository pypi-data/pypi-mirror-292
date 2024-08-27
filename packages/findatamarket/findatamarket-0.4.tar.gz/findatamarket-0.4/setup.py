from setuptools import setup, find_packages

setup(
    name="findatamarket",  # The name of your package
    version="0.4",
    author="Serkin Alexander",
    author_email="serkin.alexander@gmail.com",
    description="A simple package with findata function",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/serkin/findata-market",  # Replace with your package's URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

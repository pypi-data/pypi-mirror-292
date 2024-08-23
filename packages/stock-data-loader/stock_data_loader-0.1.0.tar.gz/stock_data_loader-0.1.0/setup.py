from setuptools import setup, find_packages

setup(
    name="stock_data_loader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A library for loading stock data from Seeking Alpha API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock_data_loader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi-quickstart-genesis",
    version="0.1.3",
    author="JCN",
    author_email="ackmanb@gmail.com",
    description="A quick start tool for FastAPI projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ackmanb/fastapi-quickstart",
    packages=find_packages(),
    include_package_data=True,
    package_data={"fastapi_quickstart": ["templates/*"]},
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "fastapi-quickstart=fastapi_quickstart.main:main",
        ],
    },
)

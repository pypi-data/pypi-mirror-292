# FastAPI QuickStart

FastAPI QuickStart is a tool to quickly set up a basic structure for a FastAPI application.

## Installation

```
pip install fastapi-quickstart-genesis
```

## Usage

To create a new FastAPI project structure:

```
python -m fastapi_quickstart my_app
```

This will create a new directory `my_app` with a basic FastAPI application structure.

## Project Structure

The generated project will have the following structure:

```
my_app/
├── app/
│   ├── main.py
│   └── models.py
├── tests/
└── requirements.txt
```

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment `cd venv\Scripts\activate`
4. Install development dependencies: `pip install -r requirements.txt`
5. Install the package in editable mode: `pip install -e .`

## License

This project is licensed under the MIT License.

## Build wheel

1. First, let's install the necessary tools: `pip install setuptools wheel twine`
2. Now, let's try building the distribution files again: `python setup.py sdist bdist_wheel`
3. Before uploading to PyPI, it's a good practice to check your package: `twine check dist/*`
4. If everything looks good, you can upload to PyPI: `twine upload dist/*`

You'll be prompted for your PyPI username and password. If you haven't registered on PyPI yet, you'll need to do that first at https://pypi.org/account/register/

5. After uploading, you can install your package using pip: `pip install fastapi-quickstart-genesis`
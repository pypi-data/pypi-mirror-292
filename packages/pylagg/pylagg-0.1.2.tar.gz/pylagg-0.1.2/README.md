# LAGG
A CLI tool for generating chaos graphs from DNA sequences.


## For Contributors
All of the following instructions requires that you type `cd backend` so that your terminal points to backend directory.

### Install Dependencies
Install [Poetry](https://python-poetry.org) on your system.
Installation instructions can be found [here](https://python-poetry.org/docs/#installation).

Use `poetry install` to install all dependencies automatically in a new virtual environment.
If you'd like to install the dependencies directly within the project directory, type the following command:
```
poetry config virtualenvs.in-project true
```

### Running the API
To run the API, first, activate the virtual environment using `poetry shell`.

Use `python main.py` to run the backend API.
Add `/docs` to the end of the given URL to see the OpenAPI docs and run the endpoints.

### Running Tests
To run tests, first, activate the virtual environment using `poetry shell`.

Use `pytest` to run all tests in the backend.

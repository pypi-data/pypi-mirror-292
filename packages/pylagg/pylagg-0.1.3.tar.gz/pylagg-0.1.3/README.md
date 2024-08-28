# LAGG
A CLI tool for generating chaos graphs from DNA sequences.


## For Contributors
We use [Poetry](https://python-poetry.org) to handle dependencies and build the project.
Installation instructions can be found [here](https://python-poetry.org/docs/#installation).

### Install Dependencies
Use `poetry install` to install all dependencies automatically in a new virtual environment.
If you'd like to install the dependencies directly within the project directory, type the following command:
```
poetry config virtualenvs.in-project true
```

### Running Tests
To run tests, first, activate the virtual environment using `poetry shell`.

Use `pytest` to run all tests in the backend.

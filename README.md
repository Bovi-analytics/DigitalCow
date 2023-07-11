# Cow-builder v1.0

## Getting started

The basic installation will install all dependencies required 
to run a simulation using the cow builder package.

Install the cow-builder package using pip:

    pip install git+https://github.com/Bovi-analytics/cow-builder@main

Or add it to your ``requirements.txt``:

    cow-builder @ git+https://github.com/Bovi-analytics/cow-builder@main

Alternatively, extra dependencies can be installed alongside the required dependencies:

* The developer installation will install additional dependencies used to update the documentation.
* The visualisation installation will install packages that can be used to visualise results.

Below the commands can be found to install each installation. If you want to install all optional dependencies, 
both commands should be executed.

developer dependencies:

    pip install -e git+https://github.com/Bovi-analytics/cow-builder@main#egg=cow-builder[dev]

visualisation dependencies:

    pip install -e git+https://github.com/Bovi-analytics/cow-builder@main#egg=cow-builder[visualisation]

or add them to your ``requirements.txt``:

developer dependencies:

    cow-builder[dev] @ git+https://github.com/Bovi-analytics/cow-builder@main

visualisation dependencies:

    cow-builder[visualisation] @ git+https://github.com/Bovi-analytics/cow-builder@main

## Contents

* A report introducing and describing the cow-builder package can be found in here as a PDF.
* Source code is available in the ``src/`` directory.
* Testing modules used to test the equations of phenotypes discussed in the report can be found in the ``plotting_modules/`` directory.
* Default transition matrices can be found in the ``transition_matrices/`` directory.
* The Jupyter Notebook ``main.ipynb`` contains sample code as described in the documentation.

## Contributing

This package was written in Python version 3.10.10. You can contribute to this project by cloning the git repository:

    git clone https://github.com/Bovi-analytics/cow-builder.git
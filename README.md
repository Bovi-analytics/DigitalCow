# Cow-builder

## Getting started

The basic installation will install all dependencies required 
to run a simulation using the cow builder package.

Install the cow-builder package using pip:

``pip install git+https://github.com/Bovi-analytics/cow-builder@main``

Or add it to your ``requirements.txt``:

``cow-builder @ git+https://github.com/Bovi-analytics/cow-builder@main``

Additional dependencies can be installed:

* The developer installation will install additional dependencies used to update the documentation.
* The visualisation installation will install ``matplotlib`` so results can be visualised.

Below the commands can be found to install each installation.

developer dependencies:

``pip install cow-builder[dev] @ git+https://github.com/Bovi-analytics/cow-builder@main``

visualisation dependencies:

``pip install cow-builder[visualisation] @ git+https://github.com/Bovi-analytics/cow-builder@main``

## Contents

* A report introducing and describing the cow-builder package can be found in here as a PDF.
* Source code is available in the ``src/`` directory.
* Testing modules used to test the equations of phenotypes discussed in the report can be found in the ``plotting_modules/`` directory.
* Default transition matrices can be found in the ``transition_matrices/`` directory.
* The Jupyter Notebook ``main.ipynb`` contains sample code as described in the documentation.

## Contributing

This package was written in Python version 3.10.10. You can contribute to this project by cloning the git repository:

``git clone https://github.com/Bovi-analytics/cow-builder.git``
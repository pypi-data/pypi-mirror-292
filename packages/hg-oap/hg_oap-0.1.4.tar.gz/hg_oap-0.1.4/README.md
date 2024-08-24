# HGraph Orders and Pricing Library

Provides a library, based on the hgraph functional reactive framework to
support creating order and pricing logic.

The core components of the library include:

* instruments
* positions
* portfolios
* orders
* pricing

This library is currently very green and is expected to have significant changes.


## Development

The project is currently configured to make use of [Hatchling](https://hatch.pypa.io/latest/) for dependency management. 
Take a look at the website to see how best to install the tool.
Once you have checked out the project, you can install the project for development using the following command:

```bash
hatch env create all.py3.11
```

Then you can find the location of the installation using:

```bash
hatch env find all.py3.11
```

For users of CLion / PyCharm, you can then add the environment by selecting an existing virtual environment using
the location above.

### Run MyPy Type Checking

```bash
hatch run types:check
```

### Run Tests

```bash
# No Coverage
hatch run test
```

```bash
# Generate Coverage Report
hatch run cov
```
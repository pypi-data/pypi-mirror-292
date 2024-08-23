# Deming Regression

This package provides a simple implementation of Deming regression, an errors-in-variables model which tries to find the line of best fit for a two-dimensional dataset when there are errors in both the x and y variables.

## Installation

You can install the package using pip:

```
pip install deming_regression
```

## Usage

Here's a simple example of how to use the `deming_regression` function:

```python
from deming_regression import deming_regression
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = 2 * x + 1 + np.random.normal(0, 0.1, 5)

intercept, slope = deming_regression(x, y, 0.1, 0.1)
print(f"Intercept: {intercept}, Slope: {slope}")
```

## Running Tests

To run the unit tests, navigate to the package directory and run:

```
python -m unittest discover tests
```

## License

This project is licensed under the MIT License.
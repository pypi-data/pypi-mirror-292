# Introduction

Do you have a truncated triangle distribution and want to find the average value? This package calculates it for you.

## Usage

After installing truncated_triangle_distribution_mean with something like:

```
pip install truncated_triangle_distribution_mean
```
You can get the mean of the distribution like so:

```
from truncated_triangle_distribution_mean import TruncatedTriangleDistribution

lower = 1
middle = 2
upper = 3
lower_truncation = 1.1
upper_truncation = 2.8
truncated_triangle_distribution = TruncatedTriangleDistribution(
    lower, middle, upper, lower_truncation, upper_truncation
)
print(f"The mean is: {truncated_triangle_distribution.mean}.")
```

## Credit

I'd like to credit the author of this website [here](https://mantimantilla.github.io/Truncated-Triangular-Simulation-R/) for laying out the maths that this package is based on. I'd also like to let them know that they have integrated between the incorrect bounds for their third equation in the "mean" section, and I had to figure that out myself.

## Contributions

If you have any problems, raise an issue on Github or send me an email. If you want to contribute, just submit a pull request. To set the repo up for development, clone it down and run:

```
pip install -e.[dev]
```

and install the pre-commit with `pre-commit install`.
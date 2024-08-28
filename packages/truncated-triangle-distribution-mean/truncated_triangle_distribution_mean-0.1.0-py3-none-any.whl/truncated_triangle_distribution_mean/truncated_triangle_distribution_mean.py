import dataclasses


@dataclasses.dataclass
class TruncatedTriangleDistribution:
    lower: float
    middle: float
    upper: float
    lower_truncation: float
    upper_truncation: float

    def __post_init__(self):
        # Validate that the values in the variables make sense.
        if self.lower > self.middle:
            raise ValueError(
                '"lower" value of distribution is larger than the "middle" value.'
            )

        if self.middle > self.upper:
            raise ValueError(
                '"middle" value of distribution is larger than the "upper" value.'
            )

        if self.lower_truncation > self.upper_truncation:
            raise ValueError(
                '"lower_truncation" value of distribution is larger than the "upper_truncation" value.'
            )

        if self.lower_truncation > self.upper:
            raise ValueError('"lower_truncation" is >= "upper" truncating everything.')

        if self.upper_truncation < self.lower:
            raise ValueError('"upper_truncation" is <= "lower", truncating everything.')

    @classmethod
    def from_scipy(
        cls,
        c: float,
        loc: float,
        scale: float,
        lower_truncation: float | None = None,
        upper_truncation: float | None = None,
    ) -> "TruncatedTriangleDistribution":
        if c < 0 or c > 1:
            raise ValueError('"c" should be 0 <= c <= 1')

        lower = loc
        middle = loc + c * scale
        upper = loc + scale

        if lower_truncation is not None:
            modified_lower_truncation = lower_truncation
        else:
            modified_lower_truncation = lower

        if upper_truncation is not None:
            modified_upper_truncation = upper_truncation
        else:
            modified_upper_truncation = lower

        return TruncatedTriangleDistribution(
            lower=lower,
            middle=middle,
            upper=upper,
            lower_truncation=modified_lower_truncation,
            upper_truncation=modified_upper_truncation,
        )

    @property
    def mean(self) -> float:
        # Snap truncation values to lower/upper if they are outside the range
        # of [lower, upper].
        lower_truncation = max(self.lower_truncation, self.lower)
        upper_truncation = min(self.upper_truncation, self.upper)

        # I'm not 100% sure if this is mathematically the correct behaviour,
        # but I think it's either this or throw an exception...
        if lower_truncation == upper_truncation:
            return lower_truncation

        if self.lower <= lower_truncation < upper_truncation <= self.middle:
            return (
                2
                * (
                    upper_truncation**3
                    - lower_truncation**3
                    - 3
                    * self.lower
                    * (upper_truncation**2 / 2 - lower_truncation**2 / 2)
                )
                / (3 * (self.upper - self.lower) * (self.middle - self.lower))
                / self.get_normalizing_factor()
            )

        if (
            self.lower
            <= lower_truncation
            < self.middle
            < upper_truncation
            <= self.upper
        ):
            return (
                (
                    -(self.middle**3) * self.upper
                    - 2 * lower_truncation**3 * self.upper
                    + 3 * self.lower * lower_truncation**2 * self.upper
                    + 3 * self.middle * upper_truncation**2 * self.upper
                    - 3 * self.lower * upper_truncation**2 * self.upper
                    + self.lower * self.middle**3
                    + 2 * self.middle * lower_truncation**3
                    - 3 * self.lower * self.middle * lower_truncation**2
                    - 2 * self.middle * upper_truncation**3
                    + 2 * self.lower * upper_truncation**3
                )
                / (
                    3
                    * (self.upper - self.lower)
                    * (self.middle - self.lower)
                    * (self.upper - self.middle)
                )
                / self.get_normalizing_factor()
            )

        if self.middle <= lower_truncation <= upper_truncation <= self.upper:
            return (
                (
                    self.upper * (upper_truncation**2 - lower_truncation**2)
                    - (2 * (upper_truncation**3 - lower_truncation**3)) / 3
                )
                / ((self.upper - self.lower) * (self.upper - self.middle))
                / self.get_normalizing_factor()
            )

        raise Exception("Shouldn't ever get here.")

    def get_cdf_of_triangular_distribution(self, x: float) -> float:
        if x < self.lower:
            return 0.0

        elif self.lower <= x < self.middle:
            return (x - self.lower) ** 2 / (
                (self.upper - self.lower) * (self.middle - self.lower)
            )

        elif self.middle <= x < self.upper:
            return 1.0 - (
                (self.upper - x) ** 2
                / ((self.upper - self.lower) * (self.upper - self.middle))
            )

        else:
            return 1.0

    def get_normalizing_factor(self) -> float:
        return self.get_cdf_of_triangular_distribution(
            self.upper_truncation
        ) - self.get_cdf_of_triangular_distribution(self.lower_truncation)

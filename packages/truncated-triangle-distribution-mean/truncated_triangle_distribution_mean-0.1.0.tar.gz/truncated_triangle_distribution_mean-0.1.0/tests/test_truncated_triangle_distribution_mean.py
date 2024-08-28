import pytest
from scipy.stats import triang

from truncated_triangle_distribution_mean import TruncatedTriangleDistribution


def test_example() -> None:
    """
    A basic test to prove tests are working.
    """
    assert True


class TestErrorCases:
    def test_middle_greater_than_upper(self) -> None:
        with pytest.raises(
            ValueError,
            match='"middle" value of distribution is larger than the "upper" value.',
        ):
            TruncatedTriangleDistribution(3, 5, 4, 3, 5)

    def test_lower_greater_than_middle(self) -> None:
        with pytest.raises(
            ValueError,
            match='"lower" value of distribution is larger than the "middle" value.',
        ):
            TruncatedTriangleDistribution(4, 3, 5, 3, 5)

    def test_truncations_are_the_correct_way_around(self) -> None:
        with pytest.raises(
            ValueError,
            match='"lower_truncation" value of distribution is larger than the "upper_truncation" value.',
        ):
            TruncatedTriangleDistribution(3, 4, 5, 5, 3)

    def test_c_between_zero_and_one(self) -> None:
        with pytest.raises(
            ValueError,
            match='"c" should be 0 <= c <= 1',
        ):
            TruncatedTriangleDistribution.from_scipy(-0.5, 3, 2, 3, 5)

    def test_truncations_are_the_correct_way_around_via_scipy(self) -> None:
        with pytest.raises(
            ValueError,
            match='"lower_truncation" value of distribution is larger than the "upper_truncation" value.',
        ):
            TruncatedTriangleDistribution.from_scipy(0.5, 3, 2, 5, 3)


class TestBasicCases:
    def test_basic_usage(self) -> None:
        truncated_triangle_distribution = TruncatedTriangleDistribution(3, 4, 5, 3, 5)
        assert truncated_triangle_distribution.mean == 4

    def test_basic_scipy_usage(self) -> None:
        truncated_triangle_distribution = TruncatedTriangleDistribution.from_scipy(
            0.5, 3, 2, 3, 5
        )
        assert truncated_triangle_distribution.mean == 4

    def test_skewed_but_not_truncated_distribution(self) -> None:
        a = 1.0
        b = 2.5
        c = 3.0
        truncated_triangle_distribution = TruncatedTriangleDistribution(a, b, c, a, c)
        assert truncated_triangle_distribution.mean == (a + b + c) / 3

    def test_right_angle_triangle_left(self) -> None:
        a = 1.0
        b = 1.0
        c = 3.0
        truncated_triangle_distribution = TruncatedTriangleDistribution(a, b, c, a, c)

        # Need to use pytest.approx because of float rounding:
        # 1.666666666666667 vs
        # 1.6666666666666667
        assert truncated_triangle_distribution.mean == pytest.approx((a + b + c) / 3)

    def test_right_angle_triangle_right(self) -> None:
        a = 1.0
        b = 3.0
        c = 3.0
        truncated_triangle_distribution = TruncatedTriangleDistribution(a, b, c, a, c)
        assert truncated_triangle_distribution.mean == pytest.approx((a + b + c) / 3)

    def test_all_values_the_same(self) -> None:
        truncated_triangle_distribution = TruncatedTriangleDistribution(1, 1, 1, 1, 1)
        assert truncated_triangle_distribution.mean == pytest.approx(1.0)

    def test_both_truncation_values_are_the_same(self) -> None:
        assert TruncatedTriangleDistribution(1, 2, 3, 1, 1).mean == pytest.approx(1.0)
        assert TruncatedTriangleDistribution(1, 2, 3, 2, 2).mean == pytest.approx(2.0)
        assert TruncatedTriangleDistribution(1, 2, 3, 3, 3).mean == pytest.approx(3.0)

    def test_distribution_below_zero(self) -> None:
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            -3, -2, -1, -3, -1
        )
        assert truncated_triangle_distribution.mean == -2

    def test_entire_distribution_truncated_because_upper_truncation_is_too_low(
        self,
    ) -> None:
        with pytest.raises(
            ValueError, match='"upper_truncation" is <= "lower", truncating everything.'
        ):
            TruncatedTriangleDistribution(2, 3, 4, 0, 1)

    def test_entire_distribution_truncated_because_lower_truncation_is_too_high(
        self,
    ) -> None:
        with pytest.raises(
            ValueError, match='"lower_truncation" is >= "upper" truncating everything.'
        ):
            TruncatedTriangleDistribution(2, 3, 4, 5, 6)


class TestTruncatedViaSampling:
    """
    In these tests, I test that the mean calculation is correct by just
    manually sampling the truncated distribution a million times and checking
    the mean manually.

    Testing by taking a bunch of samples isn't really a great practice, since
    it takes a long time, and isn't actually a rigorous proof of anything.
    However, with not other more authoritative packages to check against, it's
    good verification that the maths has been implemented correctly.
    """

    def test_case_a(self) -> None:
        """
            upper_truncation
                     │
        lower        │           middle                    upper
          │          │             │                        │
          │          │             │                        │
        """
        lower = 1
        middle = 2
        upper = 3
        lower_truncation = 1
        upper_truncation = 1.5
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_b(self) -> None:
        """
            lower_truncation
                     │
        lower        │           middle                    upper
          │          │             │                        │
          │          │             │                        │
        """
        lower = 1
        middle = 2
        upper = 3
        lower_truncation = 1.2
        upper_truncation = 10
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_c(self) -> None:
        """
               upper_truncation   lower_truncation
                     │                    │
        lower        │                    │     middle     upper
          │          │                    │       │         │
          │          │                    │       │         │
        """
        lower = 1
        middle = 3
        upper = 4
        lower_truncation = 0.5
        upper_truncation = 2.5
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_d(self) -> None:
        """
               upper_truncation   lower_truncation
                     │                    │
        lower        │       middle       │        upper
          │          │         │          │         │
          │          │         │          │         │
        """
        lower = 2
        middle = 3
        upper = 4
        lower_truncation = 2.2
        upper_truncation = 3.7
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_e(self) -> None:
        """
                        upper_truncation lower_truncation
                              │                  │
        lower      middle     │                  │  upper
          │          │        │                  │   │
          │          │        │                  │   │
        """
        lower = 2
        middle = 2.5
        upper = 4
        lower_truncation = 2.7
        upper_truncation = 3.7
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_f(self) -> None:
        """
                        lower_truncation
                              │
        lower      middle     │        upper
          │          │        │         │
          │          │        │         │
        """
        lower = 2.7
        middle = 3
        upper = 4
        lower_truncation = 3.1
        upper_truncation = 5.0
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_g(self) -> None:
        """
                        upper_truncation
                              │
        lower      middle     │        upper
          │          │        │         │
          │          │        │         │
        """
        lower = 2
        middle = 3
        upper = 4
        lower_truncation = 1
        upper_truncation = 3.8
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_h(self) -> None:
        """
                       upper_truncation &
                              middle
                                │
        lower_truncation &      │
              lower             │             upper
                │               │              │
                │               │              │
        """
        lower = 1
        middle = 2
        upper = 3
        lower_truncation = 1
        upper_truncation = 2
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_i(self) -> None:
        """
                  lower_truncation &
                        middle
                          │
                          │     upper_truncation &
        lower             │             upper
          │               │              │
          │               │              │
        """
        lower = 1
        middle = 2
        upper = 3
        lower_truncation = 2
        upper_truncation = 3
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_j(self) -> None:
        """
               lower &
        lower_truncation &
                 │                 middle &
                 │           upper_truncation &
                 │                  upper
                 │                   │
                 │                   │
        """
        lower = 1
        middle = 2
        upper = 2
        lower_truncation = 1
        upper_truncation = 2
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)

    def test_case_k(self) -> None:
        """
               lower &
        lower_truncation &
               middle
                 │
                 │           upper_truncation &
                 │                  upper
                 │                   │
                 │                   │
        """
        lower = 1
        middle = 1
        upper = 3
        lower_truncation = 1
        upper_truncation = 3
        truncated_triangle_distribution = TruncatedTriangleDistribution(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        sampled_mean = get_sampled_mean(
            lower, middle, upper, lower_truncation, upper_truncation
        )
        assert truncated_triangle_distribution.mean == pytest.approx(sampled_mean, 1e-3)


def get_sampled_mean(
    lower: float,
    middle: float,
    upper: float,
    lower_truncation: float,
    upper_truncation: float,
) -> float:
    # Calculate c, loc, and scale so we can make a scipy triangular distribution.
    loc = lower
    scale = upper - lower
    c = (middle - lower) / (upper - lower)

    # Make distribution
    dist = triang(c, loc, scale)
    samples = dist.rvs(size=1_000_000)

    # Remove values above lower truncation and above the upper truncation
    truncated_samples = samples[
        (samples < upper_truncation) & (samples > lower_truncation)
    ]

    # If we have removed more then 90% of the values, raise, because less
    # samples will make our average less accurate, and 100_000 samples is still
    # a good amount.
    print(len(truncated_samples))
    if len(truncated_samples) < 100_000:
        raise Exception("Truncating too many numbers. Accuracy of test reduced.")

    return truncated_samples.mean()

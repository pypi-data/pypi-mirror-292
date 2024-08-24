from collections.abc import Iterable
from enum import Enum
from functools import reduce
from numpy import abs, around, exp, float64, inf, pi, sign, sqrt
from numpy.typing import NDArray
from typing import Optional, Union


def calc_z_critical(
    confidence_interval: float,
    n_sided: int = 2
) -> float64:
    """
    Calculate the z-critical value from the confidence interval.

    Parameters
    ----------
    confidence_interval : float
        The confidence interval as a percentage between 0 and 100%.
    n_sided : int, optional
        The number of tails (default value = `2`).

    Returns
    -------
    float64
        The z-critical value as a floating point between 0 and infinity.
    """
    alpha = 1 - confidence_interval / 100
    return _normal_ppf(1 - alpha / n_sided)


def _normal_ppf(q: float64, tol: float64 = 1e-10) -> float64:
    """
    Calculates the percent point function (PPF), also known as the inverse cumulative distribution function (CDF), of a
    standard normal distribution using the Newton-Raphson method.

    Parameters
    ----------
    q : float64
        The quantile at which to evaluate the PPF.
    tol : float64, optional
        The tolerance for the Newton-Raphson method. Defaults to 1e-10.

    Returns
    -------
    float64
        The PPF value at the given quantile.
    """
    INITIAL_GUESS = 0
    MAX_ITER = 100

    def step(x):
        """Perform one step of the Newton-Raphson method."""
        x_new = x - (_normal_cdf(x) - q) / _normal_pdf(x)
        return x_new if abs(x_new - x) >= tol else x

    return (
        inf if q == 1 else
        -inf if q == 0 else
        reduce(lambda x, _: step(x), range(MAX_ITER), INITIAL_GUESS)
    )


def _normal_cdf(x: float64) -> float64:
    """
    Calculates the cumulative distribution function (CDF) of a standard normal distribution for a single value using a
    custom error function (erf).

    Parameters
    ----------
    x : float64
        The point at which to evaluate the CDF.

    Returns
    -------
    float64
        The CDF value at the given point.
    """
    return 0.5 * (1 + _erf(x / sqrt(2)))


def _erf(x: float64) -> float64:
    """
    Approximates the error function of a standard normal distribution using a numerical approximation based on
    Abramowitz and Stegun formula 7.1.26.

    Parameters
    ----------
    x : float64
        The input value.

    Returns
    -------
    float64
        The approximated value of the error function.
    """
    # constants
    A_1 = 0.254829592
    A_2 = -0.284496736
    A_3 = 1.421413741
    A_4 = -1.453152027
    A_5 = 1.061405429
    P = 0.3275911

    # Save the sign of x
    sign_ = sign(x)
    x_ = abs(x)

    # A&S formula 7.1.26
    t = 1.0 / (1.0 + P * x_)
    y = 1.0 - (((((A_5 * t + A_4) * t) + A_3) * t + A_2) * t + A_1) * t * exp(-x_ * x_)

    return sign_ * y


def _normal_pdf(x: float64) -> float64:
    """
    Calculates the probability density function (PDF) of a standard normal distribution for a single value.

    Parameters
    ----------
    x : float64
        The point at which to evaluate the PDF.

    Returns
    -------
    float64
        The PDF value at the given point.
    """
    return 1 / sqrt(2 * pi) * exp(-0.5 * x**2)


def _calc_confidence_level(
    z_critical: float64,
    n_sided: int = 2
) -> float64:
    """
    Calculate the confidence interval from the z-critical value.

    Parameters
    ----------
    z_critical_value : np.float64
        The confidence interval as a floating point number between 0 and infinity.
    n_sided : int, optional
        The number of tails (default value = `2`).

    Returns
    -------
    np.float64
        The confidence interval as a percentage between 0 and 100%.
    """
    alpha = (1 - _normal_cdf(z_critical)) * n_sided
    return (1 - alpha) * 100


def calc_required_iterations_monte_carlo(
    confidence_level: float,
    precision: float,
    sd: float
) -> int:
    """
    Calculate the number of iterations required for a Monte Carlo simulation to have a desired precision, subject to a
    given confidence level.

    Parameters
    ----------
    confidence_level : float
        The confidence level, as a percentage out of 100, that the precision should be subject too (i.e., we are x%
        sure that the sample mean deviates from the true populatation mean by less than the desired precision).
    precision : float
        The desired precision as a floating point value (i.e., if the Monte Carlo simulation will be used to estimate
        `organicCarbonPerHa` to a precision of 100 kg C ha-1 this value should be 100).
    sd : float
        The standard deviation of the sample. This can be estimated by running the model 500 times (a number that does
        not take too much time to run but is large enough for the sample standard deviation to converge reasonably
        well).

    Returns
    -------
    int
        The required number of iterations.
    """
    z_critical_value = calc_z_critical(confidence_level)
    return round(((sd * z_critical_value) / precision) ** 2)


def calc_confidence_level_monte_carlo(
    n_iterations: int,
    precision: float,
    sd: float
) -> float:
    """
    Calculate the confidence level that the sample mean calculated by the Monte Carlo simulation deviates from the
    true population mean by less than the desired precision.

    Parameters
    ----------
    n_iterations : int
        The number of iterations that the Monte Carlo simulation was run for.
    precision : float
        The desired precision as a floating point value (i.e., if the Monte Carlo simulation will be used to estimate
        `organicCarbonPerHa` to a precision of 100 kg C ha-1 this value should be 100).
    sd : float
        The standard deviation of the sample.

    Returns
    -------
    float
        The confidence level, as a percentage out of 100, that the precision should be subject too (i.e., we are x%
        sure that the sample mean deviates from the true populatation mean by less than the desired precision).
    """
    return _calc_confidence_level(precision*sqrt(n_iterations)/sd)


def calc_precision_monte_carlo(
    confidence_level: float,
    n_iterations: int,
    sd: float
) -> float:
    """
    Calculate the +/- precision of a Monte Carlo simulation for a desired confidence level.

    Parameters
    ----------
    confidence_level : float
        The confidence level, as a percentage out of 100, that the precision should be subject too (i.e., we are x%
        sure that the sample mean deviates from the true populatation mean by less than the desired precision).
    n_iterations : int
        The number of iterations that the Monte Carlo simulation was run for.
    sd : float
        The standard deviation of the sample.

    Returns
    -------
    float
        The precision of the sample mean estimated by the Monte Carlo model as a floating point value with the same
        units as the estimated mean.
    """
    z_critical = calc_z_critical(confidence_level)
    return (sd*z_critical)/sqrt(n_iterations)


def calc_descriptive_stats(
    arr: NDArray,
    stats_definition: Union[Enum, str],
    axis: Optional[int] = None,
    decimals: int = 6
) -> dict:
    """
    Calculate the descriptive stats for an array row-wise, round them to specified number of decimal places and return
    them formatted for a HESTIA node.

    Parameters
    ----------
    arr : NDArray
    stats_definition : Enum | str
    axis : int | None
    decimals : int

    Returns
    -------
    float
        The precision of the sample mean estimated by the Monte Carlo model as a floating point value with the same
        units as the estimated mean.
    """
    value = around(arr.mean(axis=axis), decimals)
    sd = around(arr.std(axis=axis), decimals)
    min_ = around(arr.min(axis=axis), decimals)
    max_ = around(arr.max(axis=axis), decimals)

    rows, columns = arr.shape
    observations = (
        [rows] * columns if axis == 0
        else [columns] * rows if axis == 1
        else [arr.size]
    )

    return {
        "value": list(value) if isinstance(value, Iterable) else [value],
        "sd": list(sd) if isinstance(sd, Iterable) else [sd],
        "min": list(min_) if isinstance(min_, Iterable) else [min_],
        "max": list(max_) if isinstance(max_, Iterable) else [max_],
        "statsDefinition": stats_definition.value if isinstance(stats_definition, Enum) else stats_definition,
        "observations": observations
    }

from typing import Callable, Optional, Union

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KernelDensity

from .chart import Chart
from .utils.plots_utils import (
    _create_chart,
    _create_chart_data_agg,
    _create_chart_data_count,
    _create_chart_options,
)


def countplot(
    data: pd.DataFrame,
    x: str,
    hue: Optional[str] = None,
    dataset_options: Optional[dict] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
    zoom: bool = True,
) -> Chart:
    """
    Create a bar chart that shows the count of observations for each category.

    This function generates a countplot, which displays the number of
    occurrences for each category in a specified column of a dataframe.
    Optionally, you can differentiate counts by another categorical variable
    using the `hue` parameter.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis categories.
        hue (Optional[str]): Column name in `data` to use for color grouping.
            Defaults to None.
        dataset_options (Optional[dict]): Options for customizing the dataset's
            appearance, such as colors or labels. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.
        zoom (bool): Whether to enable zoom functionality on the chart.
            Defaults to True.

    Returns:
        Chart: An ipychart.Chart object representing the countplot.
    """
    return _create_chart(
        data_func=_create_chart_data_count,
        data_func_kwargs={"data": data, "x": x, "hue": hue},
        kind="bar",
        options_func_kwargs={"x": x, "y": "Count", "hue": hue},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=zoom,
    )


def distplot(
    data: pd.DataFrame,
    x: str,
    bandwidth: Union[float, str] = "auto",
    grid_size: int = 1000,
    dataset_options: Optional[dict] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
    zoom: bool = True,
    **kwargs,
) -> Chart:
    """
    Create a kernel density estimate (KDE) plot on a line chart.

    This function fits a univariate kernel density estimate (KDE) to the data
    and plots the resulting density curve. It can be used to visualize the
    distribution of a numeric variable.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        bandwidth (Union[float, str]): The bandwidth of the KDE. If 'auto',
            the optimal bandwidth is determined using grid search.
            Defaults to 'auto'.
        grid_size (int): Number of points to evaluate in the KDE grid.
            Defaults to 1000.
        dataset_options (Optional[dict]): Options for customizing the dataset's
            appearance, such as line width or color. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.
        zoom (bool): Whether to enable zoom functionality on the chart.
            Defaults to True.
        **kwargs: Additional keyword arguments passed to scikit-learn's
            KernelDensity.

    Returns:
        Chart: An ipychart.Chart object representing the KDE plot.
    """
    if not is_numeric_dtype(data[x]):
        raise ValueError("x must be a numeric column")
    if isinstance(bandwidth, str) and bandwidth != "auto":
        raise ValueError("bandwidth must be a float or 'auto'")

    if dataset_options is None:
        dataset_options = {}

    # Remove outliers to find max and min values for the x axis
    iqr = data[x].quantile(0.95) - data[x].quantile(0.05)

    data_truncated = data[x][
        ~(
            (data[x] < (data[x].quantile(0.05) - 0.5 * iqr))
            | (data[x] > (data[x].quantile(0.95) + 0.5 * iqr))
        )
    ]
    max_val = int(data_truncated.max()) + 1
    min_val = int(data_truncated.min())
    max_val, min_val = (
        max_val + 0.05 * abs(max_val - min_val),
        min_val - 0.05 * abs(max_val - min_val),
    )

    # Create grid for KDE
    x_grid = np.round(np.linspace(min_val, max_val, num=grid_size), 5)

    if bandwidth == "auto":
        grid = GridSearchCV(
            KernelDensity(), {"bandwidth": np.linspace(0.1, 2, 30)}, cv=5
        )
        grid.fit(data[x].dropna().to_numpy()[:, None])
        bandwidth = grid.best_params_["bandwidth"]

    kde_skl = KernelDensity(bandwidth=bandwidth, **kwargs)
    kde_skl.fit(data[x].dropna().to_numpy()[:, np.newaxis])
    pdf = np.exp(kde_skl.score_samples(x_grid[:, np.newaxis]))

    data = {
        "labels": x_grid.tolist(),
        "datasets": [
            {"data": pdf.tolist(), "pointRadius": 0, **dataset_options}
        ],
    }

    options = _create_chart_options(
        kind="line",
        options=options,
        x=x,
        y=f"Density (bandwidth: {bandwidth:.4f})",
        hue=None,
    )

    ticks_options = options["scales"]["x"].get("ticks", {})
    ticks_options.setdefault("maxTicksLimit", 10)
    ticks_options.setdefault(
        "callback",
        "function(value, index, ticks) {"
        "if (Math.abs(value) >= 1) {return Math.round(value);} "
        "else {return value.toFixed(3);}}",
    )
    options["scales"]["x"]["ticks"] = ticks_options

    return Chart(
        data=data,
        kind="line",
        options=options,
        colorscheme=colorscheme,
        zoom=zoom,
    )


def lineplot(
    data: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    agg: Union[str, Callable] = "mean",
    dataset_options: Union[dict, list, None] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
    zoom: bool = True,
) -> Chart:
    """
    Create a line chart to visualize trends over time or between categories.

    This function generates a lineplot, which connects data points with a
    line, showing the relationship between two variables. The `agg` parameter
    allows for aggregation of data when grouping by `hue`.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (str): Column name in `data` to use for the y-axis values.
        hue (Optional[str]): Column name in `data` to use for color grouping.
            Defaults to None.
        agg (Union[str, Callable]): Aggregation function to apply when
            grouping data by `hue`. Defaults to "mean".
        dataset_options (Union[dict, list, None]): Options for customizing
            the dataset's appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.
        zoom (bool): Whether to enable zoom functionality on the chart.
            Defaults to True.

    Returns:
        Chart: An ipychart.Chart object representing the lineplot.
    """
    return _create_chart(
        data_func=_create_chart_data_agg,
        data_func_kwargs={
            "data": data,
            "kind": "line",
            "x": x,
            "y": y,
            "hue": hue,
            "agg": agg,
        },
        kind="line",
        options_func_kwargs={"x": x, "y": y, "hue": hue, "agg": agg},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=zoom,
    )


def barplot(
    data: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    agg: Union[str, Callable] = "mean",
    dataset_options: Union[dict, list, None] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
    zoom: bool = True,
) -> Chart:
    """
    Create a bar chart to show data as vertical bars.

    This function generates a barplot, which displays data values as vertical
    bars. The `agg` parameter allows for aggregation of data when grouping by
    `hue`.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (str): Column name in `data` to use for the y-axis values.
        hue (Optional[str]): Column name in `data` to use for color grouping.
            Defaults to None.
        agg (Union[str, Callable]): Aggregation function to apply when grouping
            data by `hue`. Defaults to "mean".
        dataset_options (Union[dict, list, None]): Options for customizing the
            dataset's appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.
        zoom (bool): Whether to enable zoom functionality on the chart.
            Defaults to True.

    Returns:
        Chart: An ipychart.Chart object representing the barplot.
    """
    return _create_chart(
        data_func=_create_chart_data_agg,
        data_func_kwargs={
            "data": data,
            "kind": "bar",
            "x": x,
            "y": y,
            "hue": hue,
            "agg": agg,
        },
        kind="bar",
        options_func_kwargs={"x": x, "y": y, "hue": hue, "agg": agg},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=zoom,
    )


def radarplot(
    data: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    agg: Union[str, Callable] = "mean",
    dataset_options: Union[dict, list, None] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
) -> Chart:
    """
    Create a radar chart to compare multiple data points.

    This function generates a radar chart, which displays multiple data points
    and the variation between them. The `agg` parameter allows for aggregation
    of data when grouping by `hue`.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (str): Column name in `data` to use for the y-axis values.
        hue (Optional[str]): Column name in `data` to use for color grouping.
            Defaults to None.
        agg (Union[str, Callable]): Aggregation function to apply when grouping
            data by `hue`. Defaults to "mean".
        dataset_options (Union[dict, list, None]): Options for customizing the
            dataset's appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.

    Returns:
        Chart: An ipychart.Chart object representing the radar chart.
    """
    return _create_chart(
        data_func=_create_chart_data_agg,
        data_func_kwargs={
            "data": data,
            "kind": "radar",
            "x": x,
            "y": y,
            "hue": hue,
            "agg": agg,
        },
        kind="radar",
        options_func_kwargs={"x": x, "y": y, "hue": hue, "agg": agg},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=False,  # Radar charts typically do not support zoom
    )


def doughnutplot(
    data: pd.DataFrame,
    x: str,
    y: Optional[str] = None,
    agg: Union[str, Callable] = "mean",
    dataset_options: Optional[dict] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
) -> Chart:
    """
    Create a doughnut chart to show relational proportions between data.

    This function generates a doughnut chart, which is used to display the
    proportional relationships among data points. The `agg` parameter allows
    for aggregation of data when grouping by `hue`.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (Optional[str]): Column name in `data` to use for the y-axis values.
            Defaults to None.
        agg (Union[str, Callable]): Aggregation function to apply when grouping
            data. Defaults to "mean".
        dataset_options (Optional[dict]): Options for customizing the dataset's
            appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.

    Returns:
        Chart: An ipychart.Chart object representing the doughnut chart.
    """
    data_func = _create_chart_data_agg if y else _create_chart_data_count
    return _create_chart(
        data_func=data_func,
        data_func_kwargs={
            "data": data,
            "kind": "doughnut",
            "x": x,
            "y": y,
            "agg": agg,
        },
        kind="doughnut",
        options_func_kwargs={"x": x, "y": y, "hue": None, "agg": agg},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=False,  # Doughnut charts typically do not support zoom
    )


def pieplot(
    data: pd.DataFrame,
    x: str,
    y: Optional[str] = None,
    agg: Union[str, Callable] = "mean",
    dataset_options: Optional[dict] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
) -> Chart:
    """
    Create a pie chart to show relational proportions between data.

    This function generates a pie chart, which is used to display the
    proportional relationships among data points. The `agg` parameter allows
    for aggregation of data when grouping by `hue`.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (Optional[str]): Column name in `data` to use for the y-axis values.
            Defaults to None.
        agg (Union[str, Callable]): Aggregation function to apply when grouping
            data. Defaults to "mean".
        dataset_options (Optional[dict]): Options for customizing the dataset's
            appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.

    Returns:
        Chart: An ipychart.Chart object representing the pie chart.
    """
    data_func = _create_chart_data_agg if y else _create_chart_data_count
    return _create_chart(
        data_func=data_func,
        data_func_kwargs={
            "data": data,
            "kind": "pie",
            "x": x,
            "y": y,
            "agg": agg,
        },
        kind="pie",
        options_func_kwargs={"x": x, "y": y, "hue": None, "agg": agg},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=False,  # Pie charts typically do not support zoom
    )


def polarplot(
    data: pd.DataFrame,
    x: str,
    y: Optional[str] = None,
    agg: Union[str, Callable] = "mean",
    dataset_options: Optional[dict] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
) -> Chart:
    """
    Create a polar area chart to show relational proportions with equal angles.

    This function generates a polar area chart, which is used to display the
    proportional relationships among data points, with each segment having
    the same angle but varying in radius.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (Optional[str]): Column name in `data` to use for the y-axis values.
            Defaults to None.
        agg (Union[str, Callable]): Aggregation function to apply when grouping
            data. Defaults to "mean".
        dataset_options (Optional[dict]): Options for customizing the dataset's
            appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.

    Returns:
        Chart: An ipychart.Chart object representing the polar area chart.
    """
    data_func = _create_chart_data_agg if y else _create_chart_data_count
    return _create_chart(
        data_func=data_func,
        data_func_kwargs={
            "data": data,
            "kind": "polarArea",
            "x": x,
            "y": y,
            "agg": agg,
        },
        kind="polarArea",
        options_func_kwargs={"x": x, "y": y, "hue": None, "agg": agg},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=False,  # Polar area charts typically do not support zoom
    )


def scatterplot(
    data: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    dataset_options: Union[dict, list, None] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
    zoom: bool = True,
) -> Chart:
    """
    Create a scatter chart to show the relationship between two variables.

    This function generates a scatterplot, which displays individual data
    points based on two variables, with the option to differentiate points by
    a third variable using the `hue` parameter.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (str): Column name in `data` to use for the y-axis values.
        hue (Optional[str]): Column name in `data` to use for color grouping.
            Defaults to None.
        dataset_options (Union[dict, list, None]): Options for customizing the
            dataset's appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.
        zoom (bool): Whether to enable zoom functionality on the chart.
            Defaults to True.

    Returns:
        Chart: An ipychart.Chart object representing the scatterplot.
    """
    return _create_chart(
        data_func=_create_chart_data_agg,
        data_func_kwargs={
            "data": data,
            "kind": "scatter",
            "x": x,
            "y": y,
            "hue": hue,
        },
        kind="scatter",
        options_func_kwargs={"x": x, "y": y, "hue": hue},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=zoom,
    )


def bubbleplot(
    data: pd.DataFrame,
    x: str,
    y: str,
    r: str,
    hue: Optional[str] = None,
    dataset_options: Union[dict, list, None] = None,
    options: Optional[dict] = None,
    colorscheme: Optional[str] = None,
    zoom: bool = True,
) -> Chart:
    """
    Create a bubble chart to display three-dimensional data.

    This function generates a bubble chart, which is used to display
    three-dimensional data. The location of the bubble is determined by the
    first two dimensions, and the size (radius) of the bubble is determined by
    the third dimension.

    Args:
        data (pd.DataFrame): The dataframe containing the data to plot.
        x (str): Column name in `data` to use for the x-axis values.
        y (str): Column name in `data` to use for the y-axis values.
        r (str): Column name in `data` to use for the radius of the bubbles.
        hue (Optional[str]): Column name in `data` to use for color grouping.
            Defaults to None.
        dataset_options (Union[dict, list, None]): Options for customizing the
            dataset's appearance. Defaults to None.
        options (Optional[dict]): Chart.js options for configuring the chart's
            appearance and behavior. Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.
        zoom (bool): Whether to enable zoom functionality on the chart.
            Defaults to True.

    Returns:
        Chart: An ipychart.Chart object representing the bubble chart.
    """
    return _create_chart(
        data_func=_create_chart_data_agg,
        data_func_kwargs={
            "data": data,
            "kind": "bubble",
            "x": x,
            "y": y,
            "r": r,
            "hue": hue,
        },
        kind="bubble",
        options_func_kwargs={"x": x, "y": y, "hue": hue},
        dataset_options=dataset_options,
        options=options,
        colorscheme=colorscheme,
        zoom=zoom,
    )

from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
from pandas.api.types import is_numeric_dtype
from pydash import merge, set_

from ..chart import Chart


def _create_chart(
    data_func: Callable[..., Dict[str, Any]],
    data_func_kwargs: Dict[str, Any],
    kind: str,
    options_func_kwargs: Dict[str, Union[str, None]],
    dataset_options: Optional[
        Union[Dict[str, Any], List[Dict[str, Any]]]
    ] = None,
    options: Optional[Dict[str, Any]] = None,
    colorscheme: Optional[str] = None,
    zoom: bool = True,
) -> Chart:
    """
    Create a chart using the specified data function and options.

    This helper function consolidates common logic for creating charts,
    reducing redundancy across different chart types. It generates the data,
    configures the chart options, and returns the chart object.

    Args:
        data_func (Callable): Function to generate the chart data.
        data_func_kwargs (Dict[str, Any]): Arguments to pass to the data
            function.
        kind (str): The type of chart to create (e.g., 'bar', 'line').
        options_func_kwargs (Dict[str, Union[str, None]]): Arguments to pass to
            the options creation function.
        dataset_options (Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]):
            Options related to the dataset object (e.g., colors, labels).
            Defaults to an empty dict.
        options (Optional[Dict[str, Any]]): Configuration options for the chart
            (e.g., axis labels, gridlines). Defaults to None.
        colorscheme (Optional[str]): The colorscheme to apply to the chart.
            Defaults to None.
        zoom (bool): Whether to enable zoom functionality on the chart.
            Defaults to True.

    Returns:
        Chart: A configured ipychart.Chart object ready for rendering.
    """
    if dataset_options is None:
        dataset_options = {}

    data = data_func(**data_func_kwargs, dataset_options=dataset_options)
    options = _create_chart_options(
        kind=kind, options=options, **options_func_kwargs
    )

    return Chart(
        data=data,
        kind=kind,
        options=options,
        colorscheme=colorscheme,
        zoom=zoom,
    )


def _create_chart_options(
    kind: str,
    x: str,
    y: str,
    hue: str,
    options: Optional[Dict[str, Any]] = None,
    agg: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare all the options to create a chart from user's input.

    Axes labels are automatically set to match the names of the columns drawn
    on the chart. Legend is also modified to match the "hue" argument.

    Args:
        kind (str): The kind of the chart.
        x (str): Column of the dataframe used as datapoints for x Axis.
        y (str): Column of the dataframe used as datapoints for y Axis.
        hue (Optional[str]): Grouping variable that will produce points with
            different colors. Defaults to None.
        options (Optional[Dict[str, Any]]): All options to configure the chart.
            This dictionary corresponds to the "options" argument of Chart.js.
            Defaults to None.
        agg (Optional[str]): The aggregator used to gather data (e.g., 'median'
            or 'mean'). Defaults to None.

    Returns:
        Dict[str, Any]: Options dictionary ready to be inputted into a Chart
            class (i.e., match ipychart options format).
    """
    agg_label = "" if not agg else f" ({agg})"
    radials = {"radar", "pie", "polarArea", "doughnut"}

    if hue:
        title_cb = (
            f"function(tooltipItem) {{"
            f"return '{x} = ' + tooltipItem[0].label + ' & {hue} = '"
            f" + tooltipItem[0].dataset.label;}};"
        )
    else:
        title_cb = (
            f"function(tooltipItem) {{"
            f"return '{x} = ' + tooltipItem[0].label;}};"
        )

    suffix_bubble = "" if kind != "bubble" else ".split(',')[1]"
    label_cb = (
        f"function(tooltipItem) {{"
        f"return '{y + agg_label} = ' + tooltipItem.formattedValue"
        f"{suffix_bubble};}};"
    )

    default_options = {
        "plugins": {
            "tooltip": {
                "enabled": True,
                "callbacks": {"title": title_cb, "label": label_cb},
            }
        }
    }

    if kind not in radials:
        scales_opt = {
            "x": {"title": {"display": True, "text": x}},
            "y": {"title": {"display": True, "text": y + agg_label}},
        }
        default_options = set_(default_options, "scales", scales_opt)
    else:
        legend_opt = {"display": True}
        default_options = set_(default_options, "plugins.legend", legend_opt)

    if hue:
        hue_label_cb = (
            f"function(chart) {{const labels = Chart.defaults.plugins."
            f"legend.labels.generateLabels(chart);labels.map(label => "
            f"{{label['text'] = '{hue} = ' + label['text'];"
            f"return label;}});return labels;}};"
        )

        default_options = set_(
            default_options,
            "plugins.legend.labels.generateLabels",
            hue_label_cb,
        )

    options = merge(default_options, options) if options else default_options

    return options


def _create_counted_data_dict(
    data: pd.DataFrame,
    x: str,
    dataset_options: Dict[str, Any],
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare an ipychart dataset with counted data from a pandas dataframe.

    Args:
        data (pd.DataFrame): The dataframe used to draw the chart.
        x (str): Column of the dataframe used as datapoints for x Axis.
        dataset_options (Dict[str, Any]): Options related to the dataset object
            (i.e., options concerning your data).
        label (Optional[str]): The label of the dataset. Defaults to None.

    Returns:
        Dict[str, Any]: Data dictionary ready to be inputted into a Chart class
            (i.e., match ipychart data format).
    """
    if is_numeric_dtype(data[x]):
        dataset = {
            "data": data[x]
            .value_counts(sort=False)
            .sort_index(ascending=True)
            .round(4)
            .tolist(),
            **dataset_options,
        }
    else:
        dataset = {
            "data": data[x]
            .value_counts(ascending=False, sort=True)
            .round(4)
            .tolist(),
            **dataset_options,
        }
    if label:
        dataset["label"] = label

    return dataset


def _create_chart_data_count(
    data: pd.DataFrame,
    x: str,
    hue: Optional[str] = None,
    dataset_options: Optional[
        Union[Dict[str, Any], List[Dict[str, Any]]]
    ] = None,
) -> Dict[str, Any]:
    """
    Prepare all the arguments to create a chart from user's input.

    Data are counted before being sent to the Chart.

    Args:
        data (pd.DataFrame): The dataframe used to draw the chart.
        x (str): Column of the dataframe used as datapoints for x Axis.
        hue (Optional[str]): Grouping variable that will produce points with
            different colors. Defaults to None.
        dataset_options (Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]):
            These are options related to the dataset object (i.e., options
            concerning your data). Defaults to {}.

    Returns:
        Dict[str, Any]: Data dictionary ready to be inputted into a Chart class
            (i.e., match ipychart data format).
    """
    if dataset_options is None:
        dataset_options = {}

    data_dict = {"datasets": []}

    if is_numeric_dtype(data[x]):
        data_dict["labels"] = (
            data[x]
            .value_counts(sort=False)
            .sort_index(ascending=True)
            .index.tolist()
        )
    else:
        data_dict["labels"] = (
            data[x].value_counts(ascending=False, sort=True).index.tolist()
        )

    if hue:
        # Create one dataset for each unique value of the hue column
        for i, v in enumerate(sorted(data[hue].unique())):
            if isinstance(dataset_options, list):
                data_dict["datasets"].append(
                    _create_counted_data_dict(
                        data=data[data[hue] == v],
                        x=x,
                        dataset_options=dataset_options[i],
                        label=str(v),
                    )
                )
            else:
                data_dict["datasets"].append(
                    _create_counted_data_dict(
                        data=data[data[hue] == v],
                        x=x,
                        dataset_options=dataset_options,
                        label=str(v),
                    )
                )
    else:
        data_dict["datasets"].append(
            _create_counted_data_dict(
                data=data, x=x, dataset_options=dataset_options
            )
        )

    return data_dict


def _create_chart_data_agg(
    data: pd.DataFrame,
    kind: str,
    x: str,
    y: str,
    r: Optional[str] = None,
    hue: Optional[str] = None,
    agg: Optional[Union[str, Callable]] = "mean",
    dataset_options: Optional[
        Union[Dict[str, Any], List[Dict[str, Any]]]
    ] = None,
) -> Dict[str, Any]:
    """
    Prepare all the arguments to create a chart from user's input.

    Data are automatically aggregated using the method specified in the "agg"
    argument before being sent to the Chart.

    Args:
        data (pd.DataFrame): The dataframe used to draw the chart.
        kind (str): The kind of the chart.
        x (str): Column of the dataframe used as datapoints for x Axis.
        y (str): Column of the dataframe used as datapoints for y Axis.
        r (Optional[str]): Column used to define the radius of the bubbles
            (only for bubble chart). Defaults to None.
        hue (Optional[str]): Grouping variable that will produce points with
            different colors. Defaults to None.
        agg (Optional[Union[str, Callable]]): The aggregator used to gather
            data (e.g., 'median' or 'mean'). Defaults to 'mean'.
        dataset_options (Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]):
            These are options related to the dataset object (i.e., options
            concerning your data). Defaults to {}.

    Returns:
        Dict[str, Any]: Data dictionary ready to be inputted into a Chart class
            (i.e., match ipychart data format).
    """
    if dataset_options is None:
        dataset_options = {}

    data_dict = {"datasets": []}

    if kind not in {"scatter", "bubble", "radar"}:
        data_dict["labels"] = (
            data[x].value_counts(ascending=True, sort=False).index.tolist()
        )

        if hue:
            for i, v in enumerate(sorted(data[hue].unique())):
                if isinstance(dataset_options, list):
                    data_dict["datasets"].append(
                        {
                            "data": data[data[hue] == v]
                            .groupby(x)[y]
                            .agg(agg)
                            .round(4)
                            .tolist(),
                            "label": str(v),
                            **dataset_options[i],
                        }
                    )
                else:
                    data_dict["datasets"].append(
                        {
                            "data": data[data[hue] == v]
                            .groupby(x)[y]
                            .agg(agg)
                            .round(4)
                            .tolist(),
                            "label": str(v),
                            **dataset_options,
                        }
                    )
        else:
            data_dict["datasets"] = [
                {
                    "data": data.groupby(x)[y].agg(agg).round(4).tolist(),
                    "label": y,
                    **dataset_options,
                }
            ]

    elif kind == "bubble":
        data_dict["labels"] = data[x].tolist()

        def row2dictxyr(row):
            return {"x": row[x], "y": row[y], "r": row[r]}

        if hue:
            for i, v in enumerate(data[hue].unique()):
                mask = data[hue] == v
                if isinstance(dataset_options, list):
                    data_dict["datasets"].append(
                        {
                            "data": data[mask]
                            .apply(row2dictxyr, axis=1)
                            .tolist(),
                            "label": str(v),
                            **dataset_options[i],
                        }
                    )
                else:
                    data_dict["datasets"].append(
                        {
                            "data": data[mask]
                            .apply(row2dictxyr, axis=1)
                            .tolist(),
                            "label": str(v),
                            **dataset_options,
                        }
                    )
        else:
            data_dict["datasets"] = [
                {
                    "data": data.apply(row2dictxyr, axis=1).tolist(),
                    **dataset_options,
                }
            ]

    elif kind == "scatter":
        data_dict["labels"] = data[x].tolist()

        def row2dictxy(row):
            return {"x": row[x], "y": row[y]}

        if hue:
            for i, v in enumerate(data[hue].unique()):
                mask = data[hue] == v
                if isinstance(dataset_options, list):
                    data_dict["datasets"].append(
                        {
                            "data": data[mask]
                            .apply(row2dictxy, axis=1)
                            .tolist(),
                            "label": str(v),
                            **dataset_options[i],
                        }
                    )
                else:
                    data_dict["datasets"].append(
                        {
                            "data": data[mask]
                            .apply(row2dictxy, axis=1)
                            .tolist(),
                            "label": str(v),
                            **dataset_options,
                        }
                    )
        else:
            data_dict["datasets"] = [
                {
                    "data": data.apply(row2dictxy, axis=1).tolist(),
                    **dataset_options,
                }
            ]

    else:
        agg_label = "" if not agg else f" ({agg})"
        data_dict["labels"] = (
            data[x].value_counts(ascending=True, sort=False).index.tolist()
        )

        if hue:
            for i, v in enumerate(data[hue].unique()):
                mask = data[hue] == v
                if isinstance(dataset_options, list):
                    data_dict["datasets"].append(
                        {
                            "data": data[mask]
                            .groupby(x)[y]
                            .agg(agg)
                            .round(4)
                            .tolist(),
                            "label": str(v),
                            **dataset_options[i],
                        }
                    )
                else:
                    data_dict["datasets"].append(
                        {
                            "data": data[mask]
                            .groupby(x)[y]
                            .agg(agg)
                            .round(4)
                            .tolist(),
                            "label": str(v),
                            **dataset_options,
                        }
                    )
        else:
            data_dict["datasets"] = [
                {
                    "data": data.groupby(x)[y].agg(agg).round(4).tolist(),
                    "label": y + agg_label,
                    **dataset_options,
                }
            ]

    return data_dict

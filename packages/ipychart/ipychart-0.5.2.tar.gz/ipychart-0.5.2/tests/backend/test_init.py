import pytest
from IPython.display import display

from ipychart import Chart
from ipychart.utils.exceptions import (
    InvalidChartColorschemeError,
    InvalidChartDataError,
    InvalidChartKindError,
    InvalidChartOptionsError,
    InvalidChartZoomError,
)


def test_chart_init(sample_bar_chart, mock_comm):
    """
    Basic test to check if the Chart is initialized correctly and if any
    communication is detected by the mock_comm object.
    """
    display(sample_bar_chart)

    assert len(mock_comm.log_open) == 1
    assert len(mock_comm.log_send) == 0
    assert len(mock_comm.log_close) == 0

@pytest.mark.parametrize(
    "data,kind",
    [
        ({"datasets": [{"data": [1, 2, 3]}]}, "bar"),
        ({"datasets": [{"data": [4, 5, 6]}]}, "line"),
    ],
)
def test_chart_init_with_valid_data(data, kind):
    chart = Chart(data=data, kind=kind)
    assert chart.__class__.__name__ == "Chart"
    assert chart.kind == kind


def test_chart_init_with_none_values():
    chart = Chart(
        data={"datasets": [{"data": [1, 2, 3]}]},
        kind="bar",
        colorscheme=None,
        options=None,
        zoom=True,
    )
    assert chart.colorscheme is None
    assert chart.options == {'plugins': {'legend': False}}


def test_chart_init_with_empty_labels():
    chart = Chart(
        data={"labels": [], "datasets": [{"data": [1, 2, 3]}]}, kind="bar"
    )
    assert chart.data["labels"] == []


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"a": 1, "b": 2},
        {"datasets": "not a list"},
        {"datasets": [{"data": None}]},
    ],
)
def test_chart_init_with_invalid_data(invalid_data):
    with pytest.raises(InvalidChartDataError):
        Chart(data=invalid_data, kind="bar")


def test_chart_init_with_invalid_kind():
    with pytest.raises(InvalidChartKindError):
        Chart(data={"datasets": [{"data": [1, 2, 3]}]}, kind="foo")


@pytest.mark.parametrize(
    "invalid_options",
    [
        {"a": 1, "b": 2},
        "not a dictionary",
    ],
)
def test_chart_init_with_invalid_options(invalid_options):
    with pytest.raises(InvalidChartOptionsError):
        Chart(
            data={"datasets": [{"data": [1, 2, 3]}]},
            kind="bar",
            options=invalid_options,
        )


def test_chart_init_with_invalid_colorscheme():
    with pytest.raises(InvalidChartColorschemeError):
        Chart(
            data={"datasets": [{"data": [1, 2, 3]}]},
            kind="bar",
            colorscheme="foo",
        )


def test_chart_init_with_invalid_zoom():
    with pytest.raises(InvalidChartZoomError):
        Chart(data={"datasets": [{"data": [1, 2, 3]}]}, kind="bar", zoom="foo")

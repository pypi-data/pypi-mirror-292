import pytest

from ipychart import Chart


def test_colorscheme_overwrite_default_style():
    chart = Chart(
        data={"datasets": [{"data": [1, 2, 3]}]},
        kind="bar",
        colorscheme="tableau.Tableau20",
    )

    assert "backgroundColor" not in chart.data["datasets"][0]
    assert "borderColor" not in chart.data["datasets"][0]
    assert "borderWidth" not in chart.data["datasets"][0]
    assert "pointBackgroundColor" not in chart.data["datasets"][0]
    assert "pointBorderColor" not in chart.data["datasets"][0]


def test_default_style_one_bar_dataset(sample_bar_chart):
    ds = sample_bar_chart.data["datasets"][0]
    assert "backgroundColor" in ds
    assert "borderColor" in ds
    assert "borderWidth" in ds


def test_default_style_one_line_dataset(sample_line_chart):
    ds = sample_line_chart.data["datasets"][0]
    assert "backgroundColor" in ds
    assert "borderColor" in ds
    assert "borderWidth" in ds
    assert "pointBackgroundColor" in ds
    assert "pointBorderColor" in ds


def test_default_style_several_datasets():
    datasets = [{"data": [1, 2, 3]}, {"data": [4, 5, 6]}, {"data": [7, 8, 9]}]
    chart = Chart(data={"datasets": datasets}, kind="line")

    for ds in chart.data["datasets"]:
        assert "backgroundColor" in ds
        assert "borderColor" in ds
        assert "borderWidth" in ds
        assert "pointBackgroundColor" in ds
        assert "pointBorderColor" in ds

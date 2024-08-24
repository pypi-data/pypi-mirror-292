import os

import pytest
from IPython.display import display


def test_get_html_template(sample_bar_chart):
    html = sample_bar_chart.get_html_template()

    assert "<script src=" in html
    assert "application/vnd.jupyter.widget-state+json" in html
    assert "application/vnd.jupyter.widget-view+json" in html


def test_get_python_template(sample_bar_chart):
    python_code = sample_bar_chart.get_python_template()

    assert f"data = {sample_bar_chart.data}" in python_code
    assert f"options = {sample_bar_chart.options}" in python_code
    assert "Chart(data=data, kind='bar', options=options" in python_code


def test_to_image_valid_path(sample_bar_chart, tmpdir, mock_comm):
    temp_file = tmpdir.join("test.png")
    
    sample_bar_chart.to_image(str(temp_file))

    assert len(mock_comm.log_open) == 1
    assert len(mock_comm.log_send) == 0
    assert len(mock_comm.log_close) == 0


def test_to_image_invalid_directory(sample_bar_chart):
    with pytest.raises(FileNotFoundError):
        sample_bar_chart.to_image("/non/existent/path/test.png")


def test_to_image_directory_as_path(sample_bar_chart, tmpdir):
    with pytest.raises(ValueError):
        sample_bar_chart.to_image(tmpdir)


def test_to_html(sample_bar_chart, tmpdir):
    temp_file = tmpdir.join("test.html")
    sample_bar_chart.to_html(str(temp_file))
    assert os.path.exists(temp_file)
    assert os.path.getsize(temp_file) > 0

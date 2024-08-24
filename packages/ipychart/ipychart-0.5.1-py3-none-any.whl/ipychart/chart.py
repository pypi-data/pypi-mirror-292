import base64
import json
import os
import random
from typing import Any, Union

import ipywidgets as widgets
import numpy as np
from ipywidgets.embed import dependency_state, embed_data, embed_minimal_html
from pydash import has, merge, set_
from traitlets import Bool, Dict, Unicode, default, observe

from ._version import __version__
from .utils.constants import COLORSCHEMES, KINDS, OPTIONS
from .utils.exceptions import (
    InvalidChartColorschemeError,
    InvalidChartDataError,
    InvalidChartKindError,
    InvalidChartOptionsError,
    InvalidChartZoomError,
)
from .utils.messages import MSG_COLORSCHEME, MSG_FORMAT, MSG_KIND


class Chart(widgets.DOMWidget):
    """
    The power of Chart.js with Python.

    Official documentation : https://nicohlr.github.io/ipychart/

    Args:
        data (dict): Data to draw. This dictionary corresponds to the "data"
            argument of Chart.js.

        kind (str): Type of chart. This string corresponds to the "type"
            argument of Chart.js.

        options (dict, optional): All options to configure the chart. This
            dictionary corresponds to the "options" argument of Chart.js.
            Defaults to None.

        colorscheme (str, optional): Choose a predefined color scheme to your
            chart. Defaults to None. A list of all possible colorschemes can be
            found at:
            https://nagix.github.io/chartjs-plugin-colorschemes/colorchart.html.

        zoom (bool, optional): Allow the user to zoom on the Chart once it is
            created. Disabled for Doughnut, Pie, PolarArea and Radar Charts.
            Defaults to True.

    Raises:
        InvalidChartDataError: Raised when the chart data is invalid.
        InvalidChartKindError: Raised when the chart kind is not supported.
        InvalidChartOptionsError: Raised when chart options are invalid.
        InvalidChartColorschemeError: Raised when the colorscheme is invalid.
        InvalidChartZoomError: Raised when the zoom argument is not a boolean.

    Examples:
        Here's a basic example of how to use the `Chart` class:

        ```python
        dataset = {
            'labels': ['Data 1', 'Data 2', 'Data 3', 'Data 4',
                       'Data 5', 'Data 6', 'Data 7', 'Data 8'],
            'datasets': [{'data': [14, 22, 36, 48, 60, 90, 28, 12]}]
        }

        mychart = Chart(data=dataset, kind='bar')
        mychart
        ```
    """

    _view_name = Unicode("ChartView").tag(sync=True)
    _model_name = Unicode("ChartModel").tag(sync=True)
    _view_module = Unicode("ipychart").tag(sync=True)
    _model_module = Unicode("ipychart").tag(sync=True)
    _view_module_version = Unicode("^" + __version__).tag(sync=True)
    _model_module_version = Unicode("^" + __version__).tag(sync=True)

    _data_sync = Dict().tag(sync=True)
    _options_sync = Dict().tag(sync=True)
    _kind_sync = Unicode().tag(sync=True)
    _colorscheme_sync = Unicode(allow_none=True).tag(sync=True)
    _zoom_sync = Bool().tag(sync=True)
    _to_image_sync = Bool().tag(sync=True)
    _image_data_sync = Unicode().tag(sync=True)

    def __init__(
        self,
        data: dict,
        kind: str,
        options: Union[dict, None] = None,
        colorscheme: Union[str, None] = None,
        zoom: bool = True,
    ):
        super().__init__()

        self._data = data
        self._kind = kind
        self._options = options if options else {}
        self._colorscheme = colorscheme
        self._zoom = zoom
        self._image_file_path = None

        # Check inputs and sync to JS
        self._refresh_chart()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._refresh_chart()

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        self._kind = value
        self._refresh_chart()

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        self._refresh_chart()

    @property
    def colorscheme(self):
        return self._colorscheme

    @colorscheme.setter
    def colorscheme(self, value):
        self._colorscheme = value
        self._refresh_chart()

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = value
        self._refresh_chart()

    @default("layout")
    def _default_layout(self):
        return widgets.Layout(height="auto", align_self="stretch")

    def _refresh_chart(self):
        """
        Refresh chart data and sync it with JS.

        It checks inputted values, set some default options and style, and sync
        the chart with the JS part.
        """
        self._validate_current_arguments()
        self._set_default_inputs()
        self._set_synced_attributes()

    def _set_synced_attributes(self):
        """
        Update JavaScript-synchronized variables based on chart attributes.

        This method ensures that the attributes of the chart are synchronized
        with their corresponding JavaScript counterparts. Whenever these
        "_sync" variables are updated, their new values are automatically
        propagated to the JavaScript side of the implementation.
        """
        self._options_sync = self._options
        self._data_sync = self._data
        self._kind_sync = self._kind
        self._colorscheme_sync = self._colorscheme
        self._zoom_sync = self._zoom

    def _validate_current_arguments(self):
        """
        Validate chart arguments for Chart.js format compatibility.

        This method ensures that all arguments passed to the chart are valid
        and conform to the expected structure. It performs individual
        validation on the `data`, `kind`, `options`, `colorscheme`, and `zoom`
        arguments.

        For details on the expected structure, see:
        https://nicohlr.github.io/ipychart/user_guide/usage.html

        Raises:
            InvalidChartDataError: If any of the arguments are invalid.
        """
        self._validate_data_argument()
        self._validate_kind_argument()
        self._validate_options_argument()
        self._validate_colorscheme_argument()
        self._validate_zoom_argument()

    def _validate_data_argument(self):
        """
        Validate the `data` argument for correct structure and content.

        This method checks that the `data` argument contains the required keys
        and that its contents are correctly formatted for use with Chart.js. It
        ensures that datasets are lists and contain the necessary data.

        Raises:
            InvalidChartDataError: If the `data` argument is missing required
                elements or is incorrectly structured.
        """

        if not isinstance(self._data, dict) or self._data is None:
            raise InvalidChartDataError(
                message=MSG_FORMAT.format("data"), data=self._data
            )

        datasets = self._data.get("datasets", None)
        if not datasets or not isinstance(datasets, list):
            raise InvalidChartDataError(
                message=MSG_FORMAT.format("data['datasets']"), data=self._data
            )

        for dataset in datasets:
            if (
                not isinstance(dataset, dict)
                or "data" not in dataset
                or not isinstance(dataset["data"], list)
            ):
                raise InvalidChartDataError(
                    message=MSG_FORMAT.format("data['datasets']"), data=dataset
                )

            dataset["data"] = [
                item for item in dataset["data"] if item is not None
            ]

            if self._kind in ["bubble", "scatter"]:
                if not all(isinstance(x, dict) for x in dataset["data"]):
                    raise InvalidChartDataError(
                        message=MSG_FORMAT.format("data['datasets']"),
                        data=dataset["data"],
                    )
                if self._kind == "bubble":
                    if not all(
                        k in p
                        for k in ("x", "y", "r")
                        for p in dataset["data"]
                    ):
                        raise InvalidChartDataError(
                            message=MSG_FORMAT.format("data"),
                            data=dataset["data"],
                        )
                else:
                    if not all(
                        k in p for k in ("x", "y") for p in dataset["data"]
                    ):
                        raise InvalidChartDataError(
                            message=MSG_FORMAT.format("data"),
                            data=dataset["data"],
                        )

            if "datalabels" in dataset and not isinstance(
                dataset["datalabels"], dict
            ):
                raise InvalidChartDataError(
                    message=MSG_FORMAT.format("data"),
                    data=dataset["datalabels"],
                )

        labels = self._data.get("labels", None)
        if labels is not None and not isinstance(labels, list):
            raise InvalidChartDataError(
                message=MSG_FORMAT.format("data['labels']"), data=labels
            )

    def _validate_kind_argument(self):
        """
        Validate the `kind` argument to ensure it is a supported chart type.

        This method checks that the `kind` argument corresponds to one of the
        supported chart types defined in the `KINDS` constant.

        Raises:
            InvalidChartKindError: If the `kind` argument is not a valid chart
                type.
        """
        if self._kind not in KINDS:
            raise InvalidChartKindError(message=MSG_KIND, kind=self._kind)

    def _validate_options_argument(self):
        """
        Validate the `options` argument for correct structure and keys.

        This method ensures that the `options` argument is a dictionary and
        that it only contains valid configuration options supported by
        Chart.js.

        Raises:
            InvalidChartOptionsError: If the `options` argument is not a
                dictionary or contains unsupported keys.
        """
        if not isinstance(self._options, dict):
            raise InvalidChartOptionsError(
                message=MSG_FORMAT.format("options"), options=self._options
            )

        if not set(self._options.keys()).issubset(set(OPTIONS)):
            raise InvalidChartOptionsError(
                message=MSG_FORMAT.format("options"), options=self._options
            )

    def _validate_colorscheme_argument(self):
        """
        Validate the `colorscheme` argument to ensure it is an allowed scheme.

        This method checks that the `colorscheme` argument, if provided, is one
        of the recognized colorschemes defined in the `COLORSCHEMES` constant.

        Raises:
            InvalidChartColorschemeError: If the `colorscheme` argument is not
                recognized or valid.
        """
        if (
            self._colorscheme is not None
            and self._colorscheme not in COLORSCHEMES
        ):
            raise InvalidChartColorschemeError(
                message=MSG_COLORSCHEME,
                colorscheme=self._colorscheme,
            )

    def _validate_zoom_argument(self):
        """
        Validate the `zoom` argument to ensure it is a boolean value.

        This method checks that the `zoom` argument is a boolean, ensuring that
        the user input is correct for enabling or disabling zoom on the chart.

        Raises:
            InvalidChartZoomError: If the `zoom` argument is not a boolean.
        """
        if not isinstance(self._zoom, bool):
            raise InvalidChartZoomError(
                message=MSG_FORMAT.format("zoom"), zoom=self._zoom
            )

    def _set_default_inputs(self):
        """
        Set some default inputs to the chart.

        To see more details about options in ipychart, please check the
        official documentation:

        https://nicohlr.github.io/ipychart/user_guide/configuration.html
        """
        # Disable cartesian axis by default for some charts
        radials = ["radar", "doughnut", "polarArea", "pie"]
        default_options = {}

        # Disable legend by default for some charts
        no_legend = ["bar", "line", "bubble", "radar", "scatter"]
        if (len(self._data["datasets"]) == 1) and (self._kind in no_legend):
            default_options = set_(default_options, "plugins.legend", False)

        self._options = merge(default_options, self._options)

        # Disable zoom by default for some charts
        self._zoom = False if self._kind in radials else self._zoom

        # Set default style is colorscheme is not provided
        cs_plugin_key = "plugins.colorschemes.scheme"
        if not self._colorscheme and not has(self._options, cs_plugin_key):
            self._set_default_style()

    def _set_default_style(self):
        """
        Apply a default style to the chart.

        This method sets a default visual style for the chart when no specific
        styling options are provided by the user. It ensures that the chart is
        visually appealing by applying colors to datasets based on predefined
        color schemes and random colors. The method adapts the style based on
        the number of datasets and the type of chart being used.

        For more details on styling in ipychart, see:
        https://nicohlr.github.io/ipychart/user_guide/charts.html

        Notes:
            - For charts with a single dataset, a set of unique colors is
            applied to the data points, ensuring consistency and readability.
            - For charts with multiple datasets, each dataset is assigned a
            distinct color from a larger palette, which includes both
            predefined and random colors.
            - The method also handles specific styling details like setting the
            background color, border color, and border width for different
            types of charts.
            - If the chart type supports points (e.g., line, radar, scatter,
            bubble), it also sets the point background and border colors.

        Related Methods:
            - `_generate_random_colors`: Generates random colors used in the
            color palette.
            - `_generate_colors_all`: Combines predefined and random colors
            into a comprehensive color palette.
            - `_apply_style_to_single_dataset`: Applies styles specifically for
            charts with a single dataset.
            - `_apply_style_to_multiple_datasets`: Applies styles for charts
            with multiple datasets.
        """
        random_colors = self._generate_random_colors(100)

        # Chart.js main colors for one dataset
        colors_unique = [
            "rgba(54, 163, 235, 0.2)",
            "rgba(254, 119, 124, 0.2)",
            "rgba(255, 206, 87, 0.2)",
        ]

        # Chosen colors for the ten first datasets then random colors
        colors_all = self._generate_colors_all(colors_unique, random_colors)

        # Apply style to datasets
        if len(self._data["datasets"]) == 1:
            self._apply_style_to_single_dataset(colors_unique, colors_all)
        else:
            self._apply_style_to_multiple_datasets(colors_all)

    @staticmethod
    def _generate_random_colors(num_colors: int) -> list:
        """
        Generate a list of random RGBA color strings.

        This method creates a specified number of randomly generated RGBA color
        strings. These colors are used to ensure variety and visual distinction
        in charts with multiple datasets or data points.

        Args:
            num_colors (int): The number of random colors to generate.

        Returns:
            list: A list of RGBA color strings, each in the format
                "rgba(R, G, B, A)", where R, G, and B are random values between
                0 and 255, and A is set to 0.2 for transparency.

        Notes:
            - The method uses a combination of random sampling and NumPy's
            `choice` function to ensure that the generated colors are varied
            and vibrant.
            - This method is primarily used to create a fallback color palette
            when specific colors are not provided by the user or when the chart
            has more datasets than predefined colors.
        """
        return [
            "rgba({}, {}, {}, 0.2)".format(
                *random.sample(
                    list(np.random.choice(range(256), size=2))
                    + list(np.random.choice(range(200, 256), size=1)),
                    3,
                )
            )
            for _ in range(num_colors)
        ]

    @staticmethod
    def _generate_colors_all(colors_unique: list, random_colors: list) -> list:
        """
        Generate a comprehensive list of colors to be used across all datasets.

        This method combines a predefined list of unique colors with additional
        randomly generated colors to produce a color palette that can be used
        for multiple datasets in a chart. This ensures that each dataset can be
        distinctly colored, even if there are many datasets.

        Args:
            colors_unique (list): A list of predefined RGBA color strings that
                are used as the primary colors for the first few datasets.
            random_colors (list): A list of randomly generated RGBA color
                strings that are used to extend the color palette beyond the
                predefined colors.

        Returns:
            list: A list of RGBA color strings that combines the unique colors
                with the randomly generated ones, providing enough colors for
                multiple datasets.

        Notes:
            - The predefined colors ensure that the most common datasets have
            consistent and visually appealing colors.
            - The random colors ensure that there are enough distinct colors
            available even when the chart contains a large number of datasets.
        """
        return (
            colors_unique
            + [
                "rgba(11, 255, 238, 0.2)",
                "rgba(153, 102, 255, 0.2)",
                "rgba(255, 159, 64, 0.2)",
                "rgba(5, 169, 69, 0.2)",
                "rgba(230, 120, 199, 0.2)",
                "rgba(35, 120, 206, 0.2)",
                "rgba(211, 216, 214, 0.2)",
            ]
            + random_colors
        )

    def _apply_style_to_single_dataset(
        self, colors_unique: list, colors_all: list
    ):
        """
        Apply default styling to a single dataset in the chart.

        This method determines the appropriate colors for the dataset based on
        the type of chart. It sets the background color, border color, and
        other style properties such as border width and point colors (for line,
        radar, scatter, and bubble charts).

        Args:
            colors_unique (list): A list of unique RGBA color strings used for
                charts with a single dataset.
            colors_all (list): A list of RGBA color strings used for charts
                with multiple data points in a single dataset.

        Notes:
            - If the dataset already has specific styling defined (e.g.,
            backgroundColor or borderColor), this method will respect those
            settings and only fill in the missing styles.
            - The method handles different chart types, including line, radar,
            scatter, bubble, and bar charts, applying different logic for each.
        """
        ds = self._data["datasets"][0]
        ds_type = ds.get("type", self._kind)

        bgc = ds.get("backgroundColor", None)
        if bgc is None:
            if ds_type in ["line", "radar", "scatter", "bubble"]:
                ds["backgroundColor"] = colors_unique[0]
            elif ds_type in ["bar"]:
                size = int(len(ds["data"]))
                colors = colors_unique * (size + 1)
                ds["backgroundColor"] = colors[:size]
            else:
                ds["backgroundColor"] = colors_all[: len(ds["data"])]

        ds["borderWidth"] = ds.get("borderWidth", 1)

        if ds_type in ["line", "radar", "scatter", "bubble"]:
            ds["borderColor"] = ds.get(
                "borderColor", ds["backgroundColor"].replace("0.2", "1")
            )
            ds["pointBackgroundColor"] = ds.get(
                "pointBackgroundColor", ds["backgroundColor"]
            )
            ds["pointBorderColor"] = ds.get(
                "pointBorderColor", ds["borderColor"]
            )
        else:
            ds["borderColor"] = [
                c.replace("0.2", "1") for c in ds["backgroundColor"]
            ]

    def _apply_style_to_multiple_datasets(self, colors_all: list):
        """
        Apply default styling to multiple datasets in the chart.

        This method assigns colors and styling attributes to each dataset in
        the chart when there are multiple datasets. It ensures that each
        dataset is distinctly colored and that the appropriate styles are
        applied based on the type of chart.

        Args:
            colors_all (list): A list of RGBA color strings used to style the
                datasets. Each dataset will receive a unique color from this
                list.

        Notes:
            - The method assigns a background color, border color, and border
            width for each dataset.
            - For charts that support points (such as line, radar, scatter, and
            bubble charts), it also assigns point background and border colors.
            - The method checks if the dataset already has specific styles set
            (e.g., backgroundColor, borderColor). If not, it applies the
            default styles.
            - The method handles different chart types, including line, radar,
            scatter, bubble, and bar charts, applying appropriate logic for
            each.
        """
        for idx, ds in enumerate(self._data["datasets"]):
            ds_type = ds.get("type", self._kind)

            ds["backgroundColor"] = ds.get(
                "backgroundColor",
                colors_all[idx]
                if ds_type in ["line", "radar", "scatter", "bubble", "bar"]
                else colors_all[: len(ds["data"])],
            )

            ds["borderColor"] = ds.get(
                "borderColor",
                ds["backgroundColor"].replace("0.2", "1")
                if ds_type in ["line", "radar", "scatter", "bubble", "bar"]
                else [c.replace("0.2", "1") for c in ds["backgroundColor"]],
            )
            ds["borderWidth"] = ds.get("borderWidth", 1)

            if ds_type in ["line", "radar", "scatter", "bubble"]:
                ds["pointBackgroundColor"] = ds.get(
                    "pointBackgroundColor", ds["backgroundColor"]
                )
                ds["pointBorderColor"] = ds.get(
                    "pointBorderColor", ds["borderColor"]
                )

    def to_html(self, path):
        """
        Embed the chart widget into an HTML file at the specified path.

        For details on embedding an ipywidget, refer to:
        https://ipywidgets.readthedocs.io/en/latest/embedding.html

        Args:
            path (str): Path where the HTML file will be created.
        """
        embed_minimal_html(path, views=[self], state=dependency_state([self]))

    def get_html_template(self) -> str:
        """
        Generate HTML code to embed the chart widget.

        For details on embedding an ipywidget, refer to:
        https://ipywidgets.readthedocs.io/en/latest/embedding.html

        Returns:
            str: HTML code for embedding the chart.
        """
        html_template = (
            """<script src="https://cdnjs.cloudflare.com/ajax/libs/require."""
            """js/2.3.4/require.min.js" integrity="sha256-Ae2Vz/4ePdIu6ZyI/5"""
            """ZGsYnb+m0JlOmKPjt6XZ9JJkA=" crossorigin="anonymous">"""
            """</script>\n"""
            """<script src="https://unpkg.com/@jupyter-widgets/html-manager@"""
            """^0.18.0/dist/embed-amd.js" crossorigin="anonymous">"""
            """</script>\n\n"""
            """<script type="application/vnd.jupyter.widget-state+json">\n"""
            "{manager_state}\n"
            """</script>\n\n"""
            """<script type="application/vnd.jupyter.widget-state+json">"""
            """</script>\n\n"""
            """<script type="application/vnd.jupyter.widget-view+json">\n"""
            "{widget_views[0]}\n"
            """</script>"""
        )

        data = embed_data(views=[self])
        manager_state = json.dumps(data["manager_state"])
        widget_views = [json.dumps(view) for view in data["view_specs"]]
        rendered_template = html_template.format(
            manager_state=manager_state, widget_views=widget_views
        )

        return rendered_template

    def get_python_template(self) -> str:
        """
        Produce the Python code needed to recreate this chart.

        Returns:
            str: Python code as a string.
        """
        python_template = (
            f"data = {self._data}\n\n"
            f"options = {self._options}\n\n"
            f"mychart = Chart(data=data, kind='{self._kind}', options=options"
        )

        if self._colorscheme:
            python_template += f", colorscheme='{self._colorscheme}'"

        python_template += ")"

        return python_template

    def to_image(self, path: str) -> None:
        """
        Export the chart as an image by saving it to the specified file path.

        Args:
            path (str): The file path where the exported image will be saved.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
            ValueError: If the path is not valid for saving the file.
        """
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            raise FileNotFoundError(
                f"The directory '{directory}' does not exist."
            )

        if os.path.isdir(path):
            raise ValueError(f"The path '{path}' is a directory, not a file.")

        self._image_file_path = path
        self._to_image_sync = True

    @observe("_image_data_sync")
    def _on_image_data_changed(self, change: dict[str, Any]) -> None:
        """
        Handle updates to the image data sent from the frontend.

        This method is automatically called when the `_image_data_sync`
        variable is  updated on the frontend. It checks if there is a valid
        file path and new image data, and if so, saves the image data to the
        specified file.

        Args:
            change (dict): A dictionary containing information about the change
                event. The 'new' key contains the updated image data.
        """
        if self._image_file_path and change["new"]:
            self._save_image(change["new"])

    def _save_image(self, image_data: str) -> None:
        """
        Save the base64-encoded image data to a file.

        This method decodes the base64-encoded image data and writes it to the
        file specified by `_image_file_path`. After saving the file, it resets
        the internal state variables to be ready for the next operation.

        Args:
            image_data (str): The base64-encoded image data.
        """
        if image_data.startswith("data:image/png;base64,"):
            image_data = image_data[len("data:image/png;base64,") :]

        image_data = base64.b64decode(image_data)

        with open(self._image_file_path, "wb") as image_file:
            image_file.write(image_data)

        self._image_file_path = None
        self._image_data_sync = ""

from .messages import MSG_COLORSCHEME, MSG_FORMAT, MSG_KIND


class InvalidChartDataError(ValueError):
    """Exception raised for errors in the chart data format."""
    def __init__(self, message=None, data=None):
        if message is None:
            message = MSG_FORMAT.format("data")
        self.data = data
        super().__init__(f"{message}: {data}")

class InvalidChartKindError(ValueError):
    """Exception raised for errors in the chart kind."""
    def __init__(self, message=None, kind=None):
        if message is None:
            message = MSG_KIND
        self.kind = kind
        super().__init__(f"{message}: {kind}")

class InvalidChartOptionsError(ValueError):
    """Exception raised for errors in the chart options."""
    def __init__(self, message=None, options=None):
        if message is None:
            message = MSG_FORMAT.format("options")
        self.options = options
        super().__init__(f"{message}: {options}")

class InvalidChartColorschemeError(ValueError):
    """Exception raised for errors in the chart colorscheme."""
    def __init__(self, message=None, colorscheme=None):
        if message is None:
            message = MSG_COLORSCHEME
        self.colorscheme = colorscheme
        super().__init__(f"{message}: {colorscheme}")

class InvalidChartZoomError(ValueError):
    """Exception raised for errors in the chart zoom option."""
    def __init__(self, message=None, zoom=None):
        if message is None:
            message = MSG_FORMAT.format("zoom")
        self.zoom = zoom
        super().__init__(f"{message}: {zoom}")
# Configuration

The `options` argument of the chart allows you to configure the chart as you please. In this section, we will go through each argument of the options dictionary that you'll pass to your chart instance. Each of them allows you to configure a specific aspect of your chart.

:::tip Note
The options relative to the modification of the scales are very complete and are therefore the subject of a separate section of the documentation. You can find this section [**here**](/ipychart/user_guide/scales).
:::

## Title

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Title options</p>

By using this argument, you can add a title to your chart. There is some configuration available to modify your title:

``` py
options = {
  'plugins': {
    'title': {   
      
      'text': str or list # Title text | Default: ''
                          # If list, text is written on multiple lines 
      'display': bool # Show the title | Default: False
      'position': str # Position ('top', 'left', 'right', 'bottom') | Default: 'top'
      'font': dict # Configure font (size, style, color, family ...)
      'padding': int # Padding between rows of colored boxes | Default: 10
    }
  }
}
```

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Example</p>

Here is an example of what you can do to with the title options (not exhaustive):

:::details Click to show the code used to generate the Chart.
<br>

``` py
dataset = {
    "labels": [1500, 1600, 1700, 1750, 1800, 1850, 1900, 1950, 2000, 2050],
    "datasets": [
        {
            "data": [86, 114, 106, 106, 107, 111, 133, 221, 783, 2478],
            "label": "Africa",
        },
        {
            "data": [282, 350, 411, 502, 635, 809, 947, 1402, 3700, 5267],
            "label": "Asia",
        },
        {
            "data": [168, 170, 178, 190, 203, 276, 408, 547, 675, 734],
            "label": "Europe",
        },
        {
            "data": [40, 20, 10, 16, 24, 38, 74, 167, 508, 784],
            "label": "Latin America",
        },
        {
            "data": [6, 3, 2, 2, 7, 26, 82, 172, 312, 433],
            "label": "North America",
        },
    ],
}

options = {
    "plugins": {
        "title": {
            "display": True,
            "text": "This is a Bar Chart",
            "font": {"size": 30, "color": "black", "style": "italic"},
        }
    }
}

mychart = Chart(dataset, "bar", options=options)
mychart
```
:::

<options-title/>

## Legend

::: tip
Unlike Chart.js, ipychart will display a legend only for Charts containing more than one dataset.
:::

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Legend options</p>

With this argument, you can configure the legend of your chart.

``` py
options = {
  'plugins': {
    'legend': {   
  
      'display': bool # Show the legend | Default: True (if multiple datasets)
      'position': str # Position ('top', 'left', 'right', 'bottom') | Default: 'top'
      'align': str # Alignment ('start', 'center', 'end') | Default: 'center'
      'fullWidth': bool # Use full width of container | Default: True
      'reverse': bool # Show datasets in reverse order | Default: False
      'rtl': bool # Rendering the legends from right to left | Default: True
      
      # Nested options
      'labels': dict # See below | Default: {}
  
      # Callback functions (see below)
      'onClick': str # Function triggered on click | Default: ''
      'onHover': str # Function triggered on click | Default: ''
      'onLeave': str # Function triggered on leave | Default: ''

    }
  }
}
```

#### Callbacks functions

Some of the arguments can be filled with callback functions. A Callback function is a Javascript function inputted into the chart to do some specific actions. To learn how to use callback functions in ipychart, you can read [the callback functions section of the documentation](/ipychart/user_guide/advanced#callback-functions).

#### Labels argument

The legend label configuration is nested below the legend configuration using the `'labels'` key. It is a dictionary which allows you to configurate the appearance of the labels within the legend. It can contain the followings arguments:

``` py
options = {
  'plugins': {
    'legend': {   
      'labels': {
  
        'boxWidth': int # Width of coloured box | Default: 40   
        'font': dict # Configure font (size, style, color, family ...)
        'padding': int # Padding between rows of colored boxes | Default: 10
        'generateLabels': str # Callback function (see below) | Default: ''
        'filter': str #  Callback function (see below) | Default: ''
        'usePointStyle': bool # Use style of point in legend | Default: False
      
      }
    }
  }
}
```

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Example</p>

Here is an example of what you can do to with the legend options (not exhaustive):

:::details Click to show the code used to generate the Chart.
<br>

``` py
dataset = {
    "labels": [1500, 1600, 1700, 1750, 1800, 1850, 1900, 1950, 1999, 2050],
    "datasets": [
        {
            "data": [86, 114, 106, 106, 107, 111, 133, 221, 121, 142],
            "label": "Africa",
            "fill": False,
        },
        {
            "data": [99, 130, 64, 100, 73, 22, 88, 198, 144, 64],
            "label": "Asia",
            "fill": False,
        },
        {
            "data": [168, 170, 178, 190, 203, 200, 164, 100, 72, 85],
            "label": "Europe",
            "fill": False,
        },
        {
            "data": [40, 20, 10, 16, 24, 38, 74, 167, 80, 150],
            "label": "Latin America",
            "fill": False,
        },
        {
            "data": [56, 95, 44, 112, 215, 35, 95, 74, 64, 78],
            "label": "North America",
            "fill": False,
        },
    ],
}

options = {
    "plugins": {
        "legend": {
            "align": "end",
            "position": "right",
            "labels": {"boxWidth": 80, "fontSize": 14},
        }
    }
}

mychart = Chart(dataset, "radar", options=options)
mychart
```
:::

<options-legend/>

:::tip
You can hide or show datasets by clicking on each element of the legend.
:::

## Tooltip

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Tooltips options</p>

With this argument, you can customize the tooltips of your chart. Tooltips are the information displayed on your chart when you hover the datapoints. Here are the tooltips configuration options:

``` py
options = {
  'plugins': {   
    'tooltip': {  

      # General options
      'enabled': bool, # Are on-canvas tooltips enabled? | Default: True
      'mode': str, # Sets which elements appear in the tooltip
                   # Default: interaction.mode
      'intersect': bool, # If True, the tooltip mode applies only when the mouse
                         # position intersects with an element
                         # Default: interaction.intersect
      'position': str, # The mode for positioning the tooltip | Default: 'average'
      'backgroundColor': str, # Background color | Default: 'rgba(0, 0, 0, 0.8)'
      'titleColor': str, # Color of title text | Default: '#fff'
      'titleFont': dict, # Font dict | Default: {weight: 'bold'}
      'bodyColor': str, # Color of body text | Default: '#fff'
      'bodyFont': dict, # Font dict | Default: {}
      'footerColor': str, # Color of footer text | Default: '#fff'
      'footerFont': dict, # Font dict | Default: {weight: 'bold'}
      'padding': dict, # Padding inside the tooltip | Default: 6
      'caretPadding': int, # Extra distance to move the end of the tooltip arrow
                           # away from the tooltip point | Default: 2
      'caretSize': int, # Size, in px, of the tooltip arrow | Default: 5
      'cornerRadius': int, # Radius of tooltip corner curves | Default: 6
      'multiKeyBackground': str, # Color to draw behind the colored boxes when
                                 # multiple items are in the tooltip
                                 # Default: '#fff'
      'displayColors': bool, # If True, color boxes are shown in the tooltip
                             # Default: True
      'borderColor': str, # Color of the border | Default: 'rgba(0, 0, 0, 0)'
      'borderWidth': int, # Size of the border | Default: 0
      'rtl': bool, # True for rendering the tooltip from right to left
                   # Default: True
      'textDirection': str, # This will force the text direction 'rtl' or 'ltr'
                            # on the canvas | Default: canvas' default
      'xAlign': str, # Position of the tooltip caret in the X direction
                     # Default: ''
      'yAlign': str,  # Position of the tooltip caret in the Y direction
                      # Default: ''

      # Callbacks options
      'callbacks': 'object',  # Callback function (see below) | Default: {}
      'itemSort': str,  # Callback function (see below) | Default: ''
      'filter': str  # Callback function (see below) | Default: ''
      'external': str,  # Callback function (see below) | Default: ''

    }
  }
}
```

#### Position argument

Possible modes are:

* `'average'`: places the tooltip at the average position of the items displayed in the tooltip.
* `'nearest'`: places the tooltip at the position of the element closest to the event position.

#### Alignment

The `titleAlign`, `bodyAlign` and `footerAlign` options define the horizontal position of the text lines with respect to the tooltip box. The following values are supported:

* `'left'` (default)
* `'right'`
* `'center'`

These options are only applied to text lines. Color boxes are always aligned to the left edge.

#### Callbacks argument

The tooltips can be customized with callback functions. A Callback function is a Javascript functions inputted into the chart to do some specific actions. To learn how to use callback functions in ipychart, you can read [the callback functions section of the documentation](/ipychart/user_guide/advanced#callback-functions).

All tooltip callback functions are called with the same arguments: a `tooltip` item and the `data` object passed to the chart. Therefore, you can render tooltips using your data. All functions must return either a string or an array of strings. Arrays of strings are treated as multiple lines of text.

``` py
options = {
  'plugins': { 
    'tooltip': {   
      'callbacks': {
  
        # All of the following arguments must be filled with 
        # a callback function (i.e. a JS function). The description
        # of each arg corresponds to what the function must return.
  
        'beforeTitle': str # Text to render before the title | Default: ''
        'title': str # Text to render as the title of the tooltip | Default: ''
        'afterTitle': str # Text to render after the title | Default: ''
        'beforeBody': str # Text to render before the body section | Default: ''
        'beforeLabel': str # Text to render before an individual label. | Default: ''
                           # This will be called for each item in the tooltip
        'label': str # Text to render for an individual item in the tooltip
                     # Default: ''
        'labelColor': str # The colors to render for the tooltip item | Default: ''
        'labelTextColor': str # The colors for the text of the label for 
                              # the tooltip item | Default: ''
        'labelPointStyle': str # Returns the point style to use instead of color
                               # boxes if usePointStyle is true | Default: ''
        'afterLabel': str # Text to render after an individual label | Default: ''
        'afterBody': str # Text to render after the body section | Default: ''
        'beforeFooter': str # Text to render before the footer section | Default: ''
        'footer': str # Text to render as the footer of the tooltip | Default: ''
        'afterFooter': str # Text to render after the footer section | Default: ''
  
      }
    }
  }
}
```

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Example</p>

Here is an example of what you can do to with the tooltip's options (not exhaustive):

:::details Click to show the code used to generate the Chart.
<br>

``` py
dataset = {
    "labels": [
        "Germany",
        "Spain",
        "UK",
        "Italy",
        "Norway",
        "France",
        "Poland",
        "Portugal",
        "Sweden",
        "Ireland",
    ],
    "datasets": [
        {
            "data": [86, 114, 106, 106, 107, 111, 133, 221, 121, 142],
            "label": "First Dataset",
            "fill": False,
            "type": "line",
            "pointRadius": 7,
            "pointHoverRadius": 7,
        },
        {
            "data": [99, 130, 64, 100, 73, 22, 88, 198, 144, 64],
            "label": "Second Dataset",
        },
        {
            "data": [40, 20, 10, 16, 24, 38, 74, 167, 80, 150],
            "label": "Third Dataset",
        },
        {
            "data": [56, 95, 44, 112, 215, 35, 95, 74, 64, 78],
            "label": "Fourth Dataset",
        },
    ],
}

options = {
    "plugins": {
        "tooltip": {
            "displayColors": False,
            "titleFont": {"size": 14},
            "bodyFont": {"size": 14},
            "enabled": True,
            "callbacks": {
                "title": """function(context) {
          return "This is a custom tooltip !";
        };""",
                "label": """function(context) {
          let flags = {
            'Germany': '🇩🇪', 'Spain': '🇪🇸', 'UK': '🇬🇧',
            'Norway': '🇳🇴', 'France': '🇫🇷', 'Poland': '🇵🇱',
            'Portugal': '🇵🇹', 'Sweden': '🇸🇪',
            'Ireland': '🇮🇪', 'Italy': '🇮🇹'
          };
          if (context.dataset.type == 'line') {
            return [
              "This POINT corresponds to the country " + 
              context.label.toUpperCase() + ' ' + 
              flags[context.label],
              "and the y axis value for this POINT is: " + 
              context.parsed.y.toString()
            ];
          } else {
            return [
              "This BAR corresponds to the country " + 
              context.label.toUpperCase() + ' ' + 
              flags[context.label],
              "and the y axis value for this BAR is: " + 
              context.parsed.y.toString()
            ];
          }
        };""",
            },
        }
    }
}

mychart = Chart(dataset, "bar", options=options)
mychart
```
:::

<options-tooltips/>

:::tip
You can hover each element (bar or point) of the Chart to display the tooltips.
:::

In the example above, we used a callback function to modify the tooltip using Javascript code.

## Layout

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Layout options</p>

With this argument, you can configure the layout of your chart (i.e. the position of your chart in its HTML container, which is the output area of the cell of your notebook). The layout argument is a dictionary containing only one key, allowing you to move the chart within its container by modifying the padding around it.

``` py
options = {
  'layout': {
    'padding': int or dict # The padding to add inside the chart | Default: 0
  }
}
```

You can specify padding on each side of the chart if you use a dictionary:

``` py
options = {
  'layout': {
    'padding': {
      'left': 50,
      'right': 10,
      'top': 10,
      'bottom': 10
    }
  }
}
```


<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Example</p>

Here is an example of what you can do to with the layout padding option (not exhaustive):

:::details Click to show the code used to generate the Chart.
<br>

``` py
dataset = {
    "labels": [
        "Germany",
        "Spain",
        "UK",
        "Italy",
        "Norway",
        "France",
        "Poland",
        "Portugal",
        "Sweden",
        "Ireland",
    ],
    "datasets": [
        {
            "data": [14, 106, 16, 107, 45, 133, 109, 109, 108, 107],
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "fill": False,
            "datalabels": {
                "display": True,
                "borderRadius": 4,
                "borderWidth": 1,
                "anchor": "end",
                "align": "end",
            },
        }
    ],
}

options = {
    "layout": {"padding": {"left": 40, "right": 40, "top": 60, "bottom": 60}}
}

mychart = Chart(dataset, "line", options=options)
mychart
```
:::

<options-layout/>

As you can see, the chart now takes up less space in its container.

## Hover

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Hover options</p>

With this argument, you can configure the the behavior of your chart when it is hovered. Available options are:

``` py
options = {
  'hover': {   

    'mode': str # Sets which elements appear in the tooltip | Default: 'nearest'
    'intersect': bool # if True, the hover mode only applies when the mouse 
                      # position intersects an item on the chart | Default: True
    'axis': str # Can be set to 'x', 'y', or 'xy' to define which directions
                # are used in calculating distances | Default: 'x'
    'animationDuration': int # Duration in milliseconds it takes to animate hover 
                             # style changes. | Default: 400

  }
}
```

## Animations

<p style="font-size:1.35rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;margin-top:-3.1rem">Animations options</p>

With this argument, you can configure the animations of your chart. Available options are:

``` py
options = {
  'animations': {   

    'duration': int # Number of milliseconds for animations | Default: 1000
    'easing': str # Easing function to use | Default: 'easeOutQuart'

    # Callbacks functions (see below)
    'onProgress': str # Called on each step of an animation | Default: ''
    'onComplete': str # Called at the end of an animation | Default: ''

  }
}
```

#### Callbacks functions

Some of the arguments can be filled with callback functions. A Callback function is a Javascript function inputted into the chart to do some specific actions. To learn how to use callback functions in ipychart, you can read [the callback functions section of the documentation](/ipychart/user_guide/advanced#callback-functions).

#### Easing

Possible values are: `'linear'`, `'easeInQuad'`, `'easeOutQuad'`, `'easeInOutQuad'`, `'easeInCubic'`, `'easeOutCubic'`, `'easeInOutCubic'`, `'easeInQuart'`, `'easeOutQuart'`, `'easeInOutQuart'`, `'easeInQuint'`, `'easeOutQuint'`, `'easeInOutQuint'`, `'easeInSine'`, `'easeOutSine'`, `'easeInOutSine'`, `'easeInExpo'`, `'easeOutExpo'`, `'easeInOutExpo'`, `'easeInCirc'`, `'easeOutCirc'`, `'easeInOutCirc'`, `'easeInElastic'`, `'easeOutElastic'`, `'easeInOutElastic'`, `'easeInBack'`, `'easeOutBack'`, `'easeInOutBack'`, `'easeInBounce'`, `'easeOutBounce'`, `'easeInOutBounce'`.

Finally, we only have one option left to explore: the `'scales'` option. As it is very complete, the [next section](/ipychart/user_guide/scales) is dedicated to it.
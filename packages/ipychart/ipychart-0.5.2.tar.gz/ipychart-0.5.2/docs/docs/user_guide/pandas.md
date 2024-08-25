# Pandas Interface

## Why ?

Today, Python is one of the most popular languages for data analysis and data science. One of the reasons for Python's success in these areas is Pandas, the leading package for data manipulation with Python. This package has quickly become a must and is used by a very large number of people around the world.

It is therefore essential to be able to create visualizations directly from a Pandas dataframe. This can be done for example with Seaborn, a famous Python package for data visualization. Thanks to the interface presented in this section, it is also possible to do the same thing with ipychart.

## Usage

This interface allows you to quickly create charts from a pandas dataframe, without having to use the low-level syntax of Chart.js. We will use, in the rest of this section, a slightly processed version (extraction of the title from the name column) of the famous [titanic dataset](https://www.kaggle.com/c/titanic/data). Let's start by loading this dataset with Pandas:

```py
import pandas as pd

titanic = pd.read_csv('titanic.csv')
titanic.head()
```
<pandas-head/>

Concretely, to use ipychart's Pandas interface, we will have to call some function directly from the ipychart package. For example, to draw a bar chart using the titanic dataset, you need to execute:

```py
import ipychart as ipc

ipc.barplot(data=titanic, x='Embarked', y='Age', hue='Survived')
```

The dataset is always passed through the `data` parameter. The `x` and `y` parameters are the columns to use for the x and y axis. The `hue` parameter is used to color the bars.

<pandas-example/>

:::tip
The hue argument allows you to display a third (categorical) column of your dataframe on the chart.
:::

## Charts

You can find here all the functions of the ipychart package for usage with a pandas dataframe, each one corresponding to a type of chart. Each function returns a *Chart* object, i.e. an instance of the *Chart* class of ipychart package.

All functions have two parameters in common: `dataset_options` and `options`. The `dataset_options` parameter allows you to set the options for each dataset, as with the *Chart* class. If you don't use the `hue` parameter, the chart will have only one dataset and you will have to pass a dictionary. Otherwise, the Chart will have N datasets (each one corresponding to a distinct value of the column selected in the `hue` parameter) and you must pass a list of dictionaries. In the same way, you can use the `options` parameter to customize the Chart, like when you use the *Chart* class.

### Count

:::tip
This chart can only be created from a single column of a Pandas dataframe.
:::

The count chart shows the count of observations in each categorical bin using bars. To draw it, you must call the *count* method:

```py
ipc.countplot(data: pd.DataFrame,
              x: str,
              hue: str = None,
              horizontal: bool = False,
              dataset_options: dict = {},
              options: dict = None,
              colorscheme: str = None,
              zoom: bool = True) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **hue (optionnal): str**<br>
Grouping variable that will produce points with different colors.
- **horizontal (optionnal): bool**<br>
Draw the bar chart horizontally. Defaults to False.
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.
- **zoom (optional): bool**<br>
Allow the user to zoom on the Chart once it is created. Defaults to True.

**Example:**

```py
ipc.countplot(data=titanic, x='Embarked')
```
<pandas-count/>

### Dist

:::tip
This chart can only be created from a single column of a Pandas dataframe.
:::

Fit and plot a univariate kernel density estimate on a line chart. This chart is useful to have a representation of the distribution of the data. To draw it, you must call the *dist* method:

```py
ipc.distplot(data: pd.DataFrame,
             x: str,
             bandwidth: Union[float, str] = 'auto',
             gridsize: int = 1000, 
             dataset_options: dict = {},
             options: dict = None, 
             colorscheme: str = None,
             zoom: bool = True,
             **kwargs) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **bandwidth (optionnal): float, str**<br>
Parameter which affect how “smooth” the resulting curve is. If set to 'auto', the optimal bandwidth is found using gridsearch.
- **gridsize (optionnal): int**<br>
Number of discrete points in the evaluation grid.
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.
- **zoom (optional): bool**<br>
Allow the user to zoom on the Chart once it is created. Defaults to True.
- **kwargs (optional): dict**<br>
Other keyword arguments are passed down to scikit-learn's *KernelDensity* class. 

**Example:**

```py
ipc.distplot(data=titanic, x='Age')
```
<pandas-dist/>

### Line

A line chart is a way of plotting data points on a line. Often, it is used to show a trend in the data, or the comparison of two data sets. To draw it, you must call the *line* method:

```py
ipc.lineplot(data: pd.DataFrame,
             x: str,
             y: str,
             hue: str = None,
             agg: str = 'mean',
             dataset_options: [dict, list] = {},
             options: dict = None,
             colorscheme: str = None,
             zoom: bool = True) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **y : str**<br>
Column of the dataframe used as datapoints for y Axis.
- **hue (optionnal): str**<br>
Grouping variable that will produce points with different colors.
- **agg (optionnal): str**<br>
The aggregator used to gather data (ex: 'median' or 'mean').
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.
- **zoom (optional): bool**<br>
Allow the user to zoom on the Chart once it is created. Defaults to True.

**Example:**

```py
datalabels_arguments = {
    "display": True,
    "borderWidth": 1,
    "anchor": "end",
    "align": "end",
    "borderRadius": 5,
    "color": "#fff",
}

ipc.lineplot(
    data=titanic,
    x="Pclass",
    y="Age",
    hue="Sex",
    dataset_options={"fill": False, "datalabels": datalabels_arguments},
    colorscheme="office.Parallax6",
)
```

<pandas-line/>

### Bar

A bar chart provides a way of showing data values represented as vertical bars. It is sometimes used to show a trend in the data, and the comparison of multiple data sets side by side. To draw it, you must call the *bar* method:

```py
ipc.barplot(data: pd.DataFrame,
            x: str,
            y: str,
            hue: str = None,
            horizontal: bool = False,
            agg: str = 'mean',
            dataset_options: Union[dict, list] = {},
            options: dict = None,
            colorscheme: str = None,
            zoom: bool = True) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **y : str**<br>
Column of the dataframe used as datapoints for y Axis.
- **hue (optionnal): str**<br>
Grouping variable that will produce points with different colors.
- **horizontal (optional): bool**<br>
Draw the bar chart horizontally.
- **agg (optionnal): str**<br>
The aggregator used to gather data (ex: 'median' or 'mean').
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.
- **zoom (optional): bool**<br>
Allow the user to zoom on the Chart once it is created. Defaults to True.

**Example:**

```py
ipc.barplot(
    data=titanic,
    x="Pclass",
    y="Fare",
    hue="Sex",
    colorscheme="office.Parallax6",
)
```

<pandas-bar/>

### Radar

A radar chart is a way of showing multiple data points and the variation between them. They are often useful for comparing the points of two or more different data sets. To draw it, you must call the *radar* method:

```py
ipc.radarplot(data: pd.DataFrame,
              x: str,
              y: str,
              hue: str = None,
              agg: str = 'mean', 
              dataset_options: Union[dict, list] = {},
              options: dict = None,
              colorscheme: str = None) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **y : str**<br>
Column of the dataframe used as datapoints for y Axis.
- **hue (optionnal): str**<br>
Grouping variable that will produce points with different colors.
- **agg (optionnal): str**<br>
The aggregator used to gather data (ex: 'median' or 'mean').
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.

**Example:**

```py
ipc.radarplot(
    data=titanic,
    x='Title',
    y='Fare',
    colorscheme='office.Yellow6'
)
```

<pandas-radar/>

### Doughnut, Pie & Polar Area

Doughnut and pie charts are excellent at showing the relational proportions between data. Polar Area charts are similar to doughnut and pie charts, but each segment has the same angle - the radius of the segment differs depending on the value. 
To draw one of these charts, you must call the *doughnut* method, the *pie* method or the *polararea* method:

```py
ipc.doughnutplot(data: pd.DataFrame,
                 x: str,
                 y: str,
                 agg: str = 'mean', 
                 dataset_options: Union[dict, list] = {},
                 options: dict = None,
                 colorscheme: str = None) -> ipc.Chart
                        
ipc.pieplot(data: pd.DataFrame,
            x: str,
            y: str,
            agg: str = 'mean', 
            dataset_options: Union[dict, list] = {},
            options: dict = None,
            colorscheme: str = None) -> ipc.Chart
                        
ipc.polarplot(data: pd.DataFrame,
              x: str,
              y: str,
              agg: str = 'mean', 
              dataset_options: Union[dict, list] = {},
              options: dict = None,
              colorscheme: str = None) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **y : str**<br>
Column of the dataframe used as datapoints for y Axis.
- **agg (optionnal): str**<br>
The aggregator used to gather data (ex: 'median' or 'mean').
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.

**Example:**

```py
ipc.polarplot(
    data=titanic,
    x="Title",
    y="Fare",
    colorscheme="brewer.SetThree5"
)
```

<pandas-polararea/>

### Scatter

Scatter charts are based on basic line charts with the x axis changed to a linear axis. To draw it, you must call the *scatter* method:

```py
ipc.scatterplot(data: pd.DataFrame,
                x: str,
                y: str,
                hue: str = None,
                dataset_options: Union[dict, list] = {},
                options: dict = None,
                colorscheme: str = None,
                zoom: bool = True) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **y : str**<br>
Column of the dataframe used as datapoints for y Axis.
- **hue (optionnal): str**<br>
Grouping variable that will produce points with different colors.
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.
- **zoom (optional): bool**<br>
Allow the user to zoom on the Chart once it is created. Defaults to True.

**Example:**

```py
ipc.scatterplot(
    data=titanic,
    x="Age",
    y="Fare",
    hue="Survived",
    colorscheme="tableau.ColorBlind10",
)
```

<pandas-scatter/>

### Bubble

A bubble chart is used to display three-dimension data. The location of the bubble is determined by the first two dimensions and the corresponding horizontal and vertical axes. The third dimension is represented by the radius of the individual bubbles. To draw it, you must call the *bubble* method:

```py
ipc.bubbleplot(data: pd.DataFrame,
               x: str,
               y: str,
               r: str,
               hue: str = None,
               dataset_options: Union[dict, list] = {},
               options: dict = None,
               colorscheme: str = None,
               zoom: bool = True) -> ipc.Chart
```

- **data : pd.DataFrame**<br>
Data used to draw the chart.
- **x : str**<br>
Column of the dataframe used as datapoints for x Axis.
- **y : str**<br>
Column of the dataframe used as datapoints for y Axis.
- **r : str**<br>
Column of the dataframe used as radius for bubbles.
- **hue (optionnal): str**<br>
Grouping variable that will produce points with different colors.
- **dataset_options (optional): dict**<br>
These are options directly related to the dataset object (i.e. options concerning your data).
- **options (optional): dict**<br>
All options to configure the chart. This dictionary corresponds to the "options" argument of Chart.js.
- **colorscheme (optional): str**<br>
Colorscheme to use when drawing the chart. List of available colorscheme: link.
- **zoom (optional): bool**<br>
Allow the user to zoom on the Chart once it is created. Defaults to True.

**Example:**

```py
ipc.bubbleplot(
    data=titanic,
    x="Age",
    y="Fare",
    r="Pclass",
    hue="Survived",
    colorscheme="office.Headlines6",
)
```

<pandas-bubble/>

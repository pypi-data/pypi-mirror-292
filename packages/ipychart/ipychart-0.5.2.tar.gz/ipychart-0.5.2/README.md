<p align="center">
    <img src="./docs/docs/.vuepress/public/ipychart.png#gh-light-mode-only" width="18%">
    <img src="./docs/docs/.vuepress/public/ipychart-dark.png#gh-dark-mode-only" width="18%"><br>
    The power of Chart.js with Python
</p>

<p align="center">
    <a href="https://github.com/nicohlr/ipychart/blob/master/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/nicohlr/ipychart">
    </a>
    <a href="https://pypi.org/project/ipychart/">
        <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/nicohlr/ipychart">
    </a>
    <a href="https://mybinder.org/v2/gh/nicohlr/ipychart/master?labpath=examples">
        <img alt="Binder" src="https://mybinder.org/badge_logo.svg">
    </a>
    <a href="https://github.com/chartjs/awesome">
        <img alt="Awesome Chart.js" src="https://img.shields.io/static/v1?message=awesome&logo=awesome-lists&labelColor=fc60a8&color=494368&logoColor=white&label=%20">
    </a>
</p>

Installation
------------

You can install ipychart from your terminal using pip or conda:

```bash
# using pip
$ pip install ipychart

# using conda
$ conda install -c conda-forge ipychart
```

Documentation
------------

- [**Introduction**](https://nicohlr.github.io/ipychart/user_guide/introduction.html)
- [**Getting Started**](https://nicohlr.github.io/ipychart/user_guide/getting_started.html)
- [**Usage**](https://nicohlr.github.io/ipychart/user_guide/usage.html)
- [**Charts**](https://nicohlr.github.io/ipychart/user_guide/charts.html)
- [**Configuration**](https://nicohlr.github.io/ipychart/user_guide/configuration.html)
- [**Scales**](https://nicohlr.github.io/ipychart/user_guide/scales.html)
- [**Pandas Interface**](https://nicohlr.github.io/ipychart/user_guide/pandas.html)
- [**Advanced Features**](https://nicohlr.github.io/ipychart/user_guide/advanced.html)
- [**Developers**](https://nicohlr.github.io/ipychart/developer_guide/development_installation.html)

Usage
------------

Create charts with Python in a very similar way to creating charts using Chart.js. The charts created are fully configurable, interactive and modular and are displayed directly in the output of the the cells of your jupyter notebook environment:

![](./docs/docs/.vuepress/public/ipychart-demo.gif)

You can also create charts directly from a pandas dataframe. See the [**Pandas Interface**](https://nicohlr.github.io/ipychart/user_guide/pandas.html) section of the documentation for more details.

Development Installation 
------------

For a development installation:

    $ git clone https://github.com/nicohlr/ipychart.git
    $ cd ipychart
    $ conda install jupyterlab -c conda-forge
    $ cd ipychart/src
    $ jlpm install 
    $ cd .. 
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix ipychart
    $ jupyter nbextension enable --py --sys-prefix ipychart

References
------------

- [**Chart.js**](https://www.chartjs.org/)
- [**Ipywidgets**](https://ipywidgets.readthedocs.io/en/latest/index.html)
- [**Ipywidgets cookiecutter template**](https://github.com/jupyter-widgets/widget-ts-cookiecutter)
- [**Chart.js Datalabels**](https://github.com/chartjs/chartjs-plugin-datalabels)
- [**Chart.js Zoom**](https://github.com/chartjs/chartjs-plugin-zoom)
- [**Vuepress**](https://vuepress.vuejs.org/)
- [**GitHub Pages**](https://pages.github.com/)

License
------------

Ipychart is available under the [MIT license](https://opensource.org/licenses/MIT).
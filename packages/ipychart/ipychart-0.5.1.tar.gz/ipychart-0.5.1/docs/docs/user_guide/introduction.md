# Introduction

`ipychart` is a Python library designed for data visualization. It empowers users to craft dynamic, sophisticated, and customizable charts using Python. It's especially tailored for Data Scientists seeking an efficient method to visualize and showcase their data directly within the output cells of their Jupyter notebooks.

<p style="font-size:1.65rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;padding-bottom:.3rem;margin-top:-3.1rem;border-bottom:1px solid #eaecef;">How does it work ?</p>

`ipychart` operates as an [ipywidget](https://ipywidgets.readthedocs.io/en/stable/), a set of tools developed by the Jupyter project's creators. These widgets allow the integration of pure Javascript code within the Jupyter environment, traditionally associated with Python. This open-source bridge between Javascript and Python enables anyone to design a custom ipywidget. Leveraging this synergy between Javascript and Python, `ipychart` brings the capabilities of the [Chart.js](https://www.chartjs.org/) Javascript library to Python enthusiasts.

The API of ipychart closely mirrors that of Chart.js, aiming to provide all the features and options that Chart.js offers. Much of the information from the official Chart.js documentation can be applied to ipychart, with some adjustments to fit Python's syntax. If you're unable to find specific details in this guide, please consult the [official Chart.js documentation](https://www.chartjs.org/docs/latest/) for further clarity.

<p style="font-size:1.65rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;padding-bottom:.3rem;margin-top:-3.1rem;border-bottom:1px solid #eaecef;">Table of Contents</p>

- [**Introduction**](/ipychart/user_guide/introduction)
- [**Getting Started**](/ipychart/user_guide/getting_started)
- [**Usage**](/ipychart/user_guide/usage)
- [**Charts**](/ipychart/user_guide/charts)
- [**Configuration**](/ipychart/user_guide/configuration)
- [**Scales**](/ipychart/user_guide/scales)
- [**Pandas Interface**](/ipychart/user_guide/pandas)
- [**Advanced Features**](/ipychart/user_guide/advanced)
- [**Developers**](/ipychart/developer_guide/development_installation)

<p style="font-size:1.65rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;padding-bottom:.3rem;margin-top:-3.1rem;border-bottom:1px solid #eaecef;">Related resources</p>

The `ipychart` package's source code is hosted on GitHub: [github.com/nicohlr/ipychart](https://github.com/nicohlr/ipychart).

For a hands-on experience with ipychart, try it online using the dedicated binder linked to the ipychart-demo-notebooks repository: [**try ipychart online**](https://mybinder.org/v2/gh/nicohlr/ipychart/master?labpath=examples).

You can also quickly try ipychart in a Jupyter Notebook environment using Docker and the [set of demo notebooks from ipychart's official repository](https://github.com/nicohlr/ipychart/tree/master/examples). To do so, install Docker and execute the command below:

```sh
$ docker run -p 8888:8888 nicohlr/ipychart
```

Afterwards, navigate to `http://localhost:8888/` in your browser. Authenticate in Jupyter by copying the provided token from your terminal and entering it in the browser.

<p style="font-size:1.65rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;padding-bottom:.3rem;margin-top:-3.1rem;border-bottom:1px solid #eaecef;">References</p>

- [**Chart.js**](https://www.chartjs.org/)
- [**Ipywidgets**](https://ipywidgets.readthedocs.io/en/latest/index.html)
- [**Ipywidgets cookiecutter template**](https://github.com/jupyter-widgets/widget-ts-cookiecutter)
- [**Chart.js Datalabels**](https://github.com/chartjs/chartjs-plugin-datalabels)
- [**Chart.js Zoom**](https://github.com/chartjs/chartjs-plugin-zoom)
- [**Vuepress**](https://vuepress.vuejs.org/)
- [**GitHub Pages**](https://pages.github.com/)

<p style="font-size:1.65rem;font-weight:600;line-height:1.25!important;margin-bottom:0;padding-top:4.6rem;padding-bottom:.3rem;margin-top:-3.1rem;border-bottom:1px solid #eaecef;">License</p>

Ipychart is available under the [MIT license](https://opensource.org/licenses/MIT).
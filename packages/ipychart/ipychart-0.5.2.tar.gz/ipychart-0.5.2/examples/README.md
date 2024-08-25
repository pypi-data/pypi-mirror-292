# ipychart examples

This folder contains a set of demonstration notebooks on how to use ipychart.

### Run with Docker

To try ipychart using docker, just install docker and run the following command in your terminal:

```sh
$ docker run -p 8888:8888 nicohlr/ipychart
```

You can now open your browser and go to http://localhost:8888/. Authenticate yourself into jupyter by copying the token from your terminal and pasting it in the browser.

You can also clone the repo and build the image locally using the provided `Dockerfile`:

```sh
$ git clone https://github.com/nicohlr/ipychart.git
$ docker build -t ipychart ipychart
$ docker run -p 8888:8888 ipychart
```
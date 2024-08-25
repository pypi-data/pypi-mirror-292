FROM mcr.microsoft.com/playwright:v1.46.1-jammy

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git-all \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

RUN pip install jupyterlab

RUN git clone https://github.com/nicohlr/ipychart.git && \
    cd ipychart && \
    git checkout develop && \
    pip install .

RUN cd ipychart/tests/frontend/ && \
    jlpm install && \
    jlpm playwright install --with-deps

RUN cd ipychart/tests/frontend/ && \
    jlpm test:update

RUN mkdir -p /output && \
    cp -r ipychart/tests/frontend/tests/ipychart.test.ts-snapshots /output

# Define the command to run the container
CMD ["bash"]
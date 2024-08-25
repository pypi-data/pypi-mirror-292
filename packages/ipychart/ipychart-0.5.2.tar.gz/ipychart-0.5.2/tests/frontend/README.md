# Visual regression tests using Galata

This directory contains visual regression tests for ipychart, using Galata.

In order to run them, you need to install dependencies:

```bash
# Create an empty yarn.lock file at tests/frontend if needed
jlpm install
```

If needed, download chromium for playwright (for first install):

```bash
jlpm playwright install
```

Finally, you can run the galata tests:

```bash
jlpm test
```

If ipychart visuals change, you can re-generate reference images by running:

```bash
jlpm test:update
```

A Dockerfile is also provided to generate snapshots on a linux environment.
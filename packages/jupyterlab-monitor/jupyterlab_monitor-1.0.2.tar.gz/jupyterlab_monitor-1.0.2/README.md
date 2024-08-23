# JupyterLab Monitor

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![PyPI](https://img.shields.io/pypi/v/jupyterlab-monitor.svg)](https://pypi.org/project/jupyterlab-monitor)
[![npm](https://img.shields.io/npm/v/jupyterlab-monitor.svg)](https://www.npmjs.com/package/jupyterlab-monitor)

JupyterLab Monitor is a fork of the original JupyterLab Pioneer extension for generating and exporting JupyterLab event telemetry data.

## Getting Started

### Installing the Extension

To install the extension, execute:

```bash
pip install jupyterlab-monitor
```

### Running the Extension with Docker Compose

```bash
# Enter the configuration_examples directory and run
docker compose -p jupyterlab_monitor up --build
```

A JupyterLab application with the extension installed and configured will run on localhost:8888.

(To experiment with different exporter configurations, edit [Dockerfile](https://github.com/P0rt/jupyterlab-monitor/blob/main/configuration_examples/Dockerfile#L32-L36) and run docker compose again)

### Manual Configuration

Before starting Jupyter Lab, users need to write their own configuration files (or use the provided configuration examples) and **place them in the correct directory**.

Examples of configurations are [here](#configurations).

## Configurations

### Overview

The configuration file controls the activated events and data exporters.

To add a data exporter, users should assign a callable function along with function arguments when configuring `exporters`.

This extension provides 5 default exporters:

- [`console_exporter`](https://github.com/P0rt/jupyterlab-monitor/blob/main/jupyterlab_monitor/default_exporters.py#L22), which sends telemetry data to the browser console
- [`command_line_exporter`](https://github.com/P0rt/jupyterlab-monitor/blob/main/jupyterlab_monitor/default_exporters.py#L48), which sends telemetry data to the Python console Jupyter is running on
- [`file_exporter`](https://github.com/P0rt/jupyterlab-monitor/blob/main/jupyterlab_monitor/default_exporters.py#L76), which saves telemetry data to a local file
- [`remote_exporter`](https://github.com/P0rt/jupyterlab-monitor/blob/main/jupyterlab_monitor/default_exporters.py#L106), which sends telemetry data to a remote HTTP endpoint
- [`opentelemetry_exporter`](https://github.com/P0rt/jupyterlab-monitor/blob/main/jupyterlab_monitor/default_exporters.py#L162), which sends telemetry data via OTLP

Additionally, users can write custom exporters in the configuration file.

[The rest of the README remains unchanged, but all references to 'jupyterlab-pioneer' should be replaced with 'jupyterlab-monitor']

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyterlab-monitor
```

## Contributors

Main contributor   of this fork: [p0rt](https://github.com/P0rt)

## Link to the Original Project

This project is a fork of the [original JupyterLab Pioneer](https://github.com/educational-technology-collective/jupyterlab-pioneer).
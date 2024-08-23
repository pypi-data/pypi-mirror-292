# This file should be saved into one of the config directories provided by `jupyter --path`.

c.JupyterLabPioneerApp.exporters = [
    {
        # sends telemetry data to a remote http endpoint (AWS S3 bucket)
        "type": "remote_exporter",
        "args": {
            "id": "S3Exporter",
            "url": "https://telemetry.mentoracademy.org/telemetry-edtech-labs-si-umich-edu/dev/test-telemetry",
            "env": ["WORKSPACE_ID"],
        },
    },
    # {
    #     # sends telemetry data to a remote http endpoint (an AWS Lambda function that exports data to MongoDB)
    #     "type": "remote_exporter",
    #     "args": {
    #         "id": "MongoDBLambdaExporter",
    #         "url": "https://68ltdi5iij.execute-api.us-east-1.amazonaws.com/mongo",
    #         "params": {
    #             "mongo_cluster": "mengyanclustertest.6b83fsy.mongodb.net",
    #             "mongo_db": "telemetry",
    #             "mongo_collection": "dev",
    #         },
    #         "env": ["WORKSPACE_ID"],
    #     },
    # },
    {
        # sends telemetry data to a remote http endpoint (an AWS Lambda function that exports data to InfluxDB)
        "type": "remote_exporter",
        "args": {
            "id": "",
            "url": "",
            "params": {
                "influx_bucket": "telemetry_dev",
                "influx_measurement": "si101_fa24",
            },
        },
        "activeEvents": [
            {"name": "CellEditEvent", "logWholeNotebook": False},
        ],  # exporter's local active_events config will override global activeEvents config
    },
]

c.JupyterLabPioneerApp.activeEvents = [
    {"name": "ActiveCellChangeEvent", "logWholeNotebook": True},
    {"name": "CellAddEvent", "logWholeNotebook": True},
    {"name": "CellEditEvent", "logWholeNotebook": True},
    {"name": "CellExecuteEvent", "logWholeNotebook": True},
    {"name": "CellRemoveEvent", "logWholeNotebook": True},
    {"name": "ClipboardCopyEvent", "logWholeNotebook": True},
    {"name": "ClipboardCutEvent", "logWholeNotebook": True},
    {"name": "ClipboardPasteEvent", "logWholeNotebook": True},
    {"name": "NotebookHiddenEvent", "logWholeNotebook": True},
    {"name": "NotebookOpenEvent", "logWholeNotebook": True},
    {"name": "NotebookSaveEvent", "logWholeNotebook": True},
    {"name": "NotebookScrollEvent", "logWholeNotebook": True},
    {"name": "NotebookVisibleEvent", "logWholeNotebook": True},
]

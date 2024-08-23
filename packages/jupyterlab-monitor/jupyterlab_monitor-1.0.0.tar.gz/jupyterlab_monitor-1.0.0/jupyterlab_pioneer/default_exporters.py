"""This module provides 5 default exporters for the extension. If the exporter function name is mentioned in the configuration file or in the notebook metadata, the extension will use the corresponding exporter function when the jupyter lab event is fired.

Attributes:
    default_exporters: a map from function names to callable exporter functions::

        default_exporters: dict[str, Callable[[dict], dict or Awaitable[dict]]] = {
            "console_exporter": console_exporter,
            "command_line_exporter": command_line_exporter,
            "file_exporter": file_exporter,
            "remote_exporter": remote_exporter,
            "opentelemetry_exporter": opentelemetry_exporter,
        }
"""

import json
import os
import datetime
import uuid
import logging
from collections.abc import Callable, Awaitable
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.escape import to_unicode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_EVENT_SIZE = 300_000  # Максимальный размер события в байтах

def console_exporter(args: dict) -> dict:
    """This exporter sends telemetry data to the browser console.

    Args:
        args(dict): arguments to pass to the exporter function, defined in the configuration file (except 'data', which is gathered by the extension). It has the following structure:
            ::

                {
                    'id': # (optional) exporter id,
                    'data': # telemetry data
                }

    Returns:
        dict:
            ::

                {
                    'exporter': # exporter id or 'ConsoleExporter',
                    'message': # telemetry data
                }

    """

    return {"exporter": args.get("id") or "ConsoleExporter", "message": args["data"]}


def command_line_exporter(args: dict) -> dict:
    """This exporter sends telemetry data to the python console jupyter is running on.

    Args:
        args (dict): arguments to pass to the exporter function, defined in the configuration file (except 'data', which is gathered by the extension). It has the following structure:
            ::

                {
                    'id': # (optional) exporter id,
                    'data': # telemetry data
                }

    Returns:
        dict:
            ::

                {
                    'exporter': # exporter id or 'CommandLineExporter',
                }
    
    """

    print(args["data"])
    return {
        "exporter": args.get("id") or "CommandLineExporter",
    }


def file_exporter(args: dict) -> dict:
    """This exporter writes telemetry data to local file.

    Args:
        args (dict): arguments to pass to the exporter function, defined in the configuration file (except 'data', which is gathered by the extension). It has the following structure:
            ::

                {
                    'id': # (optional) exporter id,
                    'path': # local file path,
                    'data': # telemetry data
                }

    Returns:
        dict:
            ::

                {
                    'exporter': # exporter id or 'FileExporter',
                }
    """

    with open(args.get("path"), "a+", encoding="utf-8") as f:
        json.dump(args["data"], f, ensure_ascii=False, indent=4)
        f.write(",")
    return {
        "exporter": args.get("id") or "FileExporter",
    }

def split_payload(payload, max_size):
    serialized = json.dumps(payload)
    total_length = len(serialized)
    chunks = []
    chunk_size = max_size - 200  # Оставляем место для дополнительных полей

    for i in range(0, total_length, chunk_size):
        chunk = serialized[i:i+chunk_size]
        chunks.append(json.loads(chunk))
    
    return chunks

async def send_request(http_client, url, payload, exporter_id):
    logger.info(f"Sending request to {url}")
    request = HTTPRequest(
        url=url,
        method="POST",
        body=json.dumps(payload),
        headers=HTTPHeaders({"content-type": "application/json"}),
    )
    try:
        response = await http_client.fetch(request, raise_error=False)
        logger.info(f"Response received. Status code: {response.code}")
        return {
            "exporter": exporter_id or "RemoteExporter",
            "message": {
                "code": response.code,
                "reason": response.reason,
                "body": to_unicode(response.body),
            },
        }
    except Exception as e:
        logger.error(f"Error sending request: {str(e)}")
        return {
            "exporter": exporter_id or "RemoteExporter",
            "message": {
                "code": 500,
                "reason": "Internal Server Error",
                "body": str(e),
            },
        }

async def remote_exporter(args: dict) -> dict:
    logger.info("Starting remote_exporter function")
    http_client = AsyncHTTPClient()
    unix_timestamp = args["data"].get("eventDetail", {}).get("eventTime")
    utc_datetime = datetime.datetime.fromtimestamp(unix_timestamp/1000.0, tz=datetime.timezone.utc)
    url = args.get("url")
    if "s3" in args.get("id", "").lower():
        url = "%s/%d/%d/%d/%d" % (args.get("url"), utc_datetime.year, utc_datetime.month, utc_datetime.day, utc_datetime.hour)
    logger.info(f"Prepared URL: {url}")
    
    event_type = args["data"].get("eventDetail", {}).get("eventName", "UnknownEvent")
    payload = {
        "type": event_type,
        "data": args["data"],
        "params": args.get("params"),
        "env": [{x: os.getenv(x)} for x in args.get("env")] if (args.get("env")) else [],
    }

    payload_size = len(json.dumps(payload).encode('utf-8'))
    logger.info(f"Payload size: {payload_size} bytes")

    if payload_size <= MAX_EVENT_SIZE:
        logger.info("Sending payload in a single request")
        result = await send_request(http_client, url, payload, args.get("id"))
        logger.info(f"Response received: {json.dumps(result, indent=2)}")
        return result
    else:
        logger.info(f"Payload size ({payload_size} bytes) exceeds maximum allowed size ({MAX_EVENT_SIZE} bytes). Splitting into chunks.")
        chunks = split_payload(payload, MAX_EVENT_SIZE)
        chunk_id = str(uuid.uuid4())
        total_chunks = len(chunks)
        logger.info(f"Split into {total_chunks} chunks. Chunk ID: {chunk_id}")
        
        results = []
        for index, chunk in enumerate(chunks):
            chunk_payload = {
                "type": event_type,
                "chunk_id": chunk_id,
                "total_chunks": total_chunks,
                "chunk_index": index + 1,
                "data": chunk["data"] if "data" in chunk else chunk,
                "params": payload["params"],
                "env": payload["env"]
            }
            logger.info(f"Sending chunk {index + 1} of {total_chunks}")
            result = await send_request(http_client, url, chunk_payload, args.get("id"))
            logger.info(f"Response for chunk {index + 1}: {json.dumps(result, indent=2)}")
            results.append(result)
        
        logger.info(f"All {total_chunks} chunks sent successfully")
        return {
            "exporter": args.get("id") or "RemoteExporter",
            "message": {
                "chunks_sent": len(results),
                "results": results
            }
        }

def opentelemetry_exporter(args: dict) -> dict:
    """This exporter sends telemetry data via otlp

    """
    from opentelemetry import trace

    current_span = trace.get_current_span()
    event_detail = args['data']['eventDetail']
    notebook_state = args['data']['notebookState']
    attributes = {
        "notebookSessionId": notebook_state['sessionID'],
        'notebookPath': notebook_state['notebookPath'],
        "event": event_detail['eventName']
    }
    current_span.add_event(event_detail['eventName'], attributes=attributes)

    return {
        "exporter": args.get("id") or "OpenTelemetryExporter",
    }

default_exporters: "dict[str, Callable[[dict], dict or Awaitable[dict]]]" = {
    "console_exporter": console_exporter,
    "command_line_exporter": command_line_exporter,
    "file_exporter": file_exporter,
    "remote_exporter": remote_exporter,
    "opentelemetry_exporter": opentelemetry_exporter,
}
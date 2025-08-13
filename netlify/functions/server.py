import os
import sys
import base64
from io import BytesIO

# Ensure the project root is in the path
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(ROOT))

from app import app as flask_app


def handler(event, context):
    """Netlify Function entry point bridging API Gateway events to the Flask app."""
    # Build a minimal WSGI environment
    headers = event.get('headers') or {}
    body = event.get('body') or ''
    if event.get('isBase64Encoded'):
        body_bytes = base64.b64decode(body)
    else:
        body_bytes = body.encode('utf-8')

    raw_path = event.get('path', '/') or '/'
    # When using redirect rules that append to the function path, Netlify will send path like
    # '/.netlify/functions/server/actual_route'. Strip the function base so Flask sees '/actual_route'
    function_prefix = '/.netlify/functions/server'
    if raw_path.startswith(function_prefix):
        stripped_path = raw_path[len(function_prefix):] or '/'
    else:
        stripped_path = raw_path

    environ = {
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': headers.get('x-forwarded-proto', 'http'),
        'wsgi.input': BytesIO(body_bytes),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'PATH_INFO': stripped_path,
        'QUERY_STRING': event.get('rawQueryString', ''),
        'SERVER_NAME': headers.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': headers.get('host', '80').split(':')[-1],
        'CONTENT_LENGTH': str(len(body_bytes)),
        'CONTENT_TYPE': headers.get('content-type', ''),
    }

    for key, value in headers.items():
        environ['HTTP_' + key.upper().replace('-', '_')] = value

    status_headers = {}

    def start_response(status, response_headers, exc_info=None):
        status_headers['status'] = status
        status_headers['headers'] = response_headers
        return lambda x: None

    response_body = b''.join(flask_app.wsgi_app(environ, start_response))

    return {
        'statusCode': int(status_headers['status'].split(' ')[0]),
        'headers': {k: v for k, v in status_headers['headers']},
        'body': base64.b64encode(response_body).decode('utf-8'),
        'isBase64Encoded': True,
    }

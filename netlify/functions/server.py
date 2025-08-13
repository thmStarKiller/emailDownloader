from serverless_wsgi import handle_request
import os, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(ROOT))

from app import app

def handler(event, context):
    prefix = "/.netlify/functions/server"
    path = event.get("path") or event.get("rawPath") or "/"
    if path.startswith(prefix):
        new_path = path[len(prefix):] or "/"
        event["path"] = new_path
        if "rawPath" in event:
            event["rawPath"] = new_path
    return handle_request(app, event, context)

import sys
import os

# Add the parent directory to Python path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Global variables to capture import state
import_error_msg = None
app = None

try:
    from serverless_wsgi import handle_request
    from app import app as flask_app
    app = flask_app
except ImportError as e:
    import_error_msg = str(e)

def handler(event, context):
    if import_error_msg:
        return {
            'statusCode': 500,
            'body': f'Import error: {import_error_msg}. Working dir: {os.getcwd()}, Files: {os.listdir(".")}'
        }
    
    # Strip Netlify function prefix from path
    path = event.get("path", "/")
    if path.startswith("/.netlify/functions/server"):
        event["path"] = path[len("/.netlify/functions/server"):] or "/"
    
    # Ensure headers exist
    if "headers" not in event:
        event["headers"] = {}
    
    # Handle both v1 and v2 API Gateway event formats
    if "rawPath" in event:
        event["rawPath"] = event["path"]
    
    return handle_request(app, event, context)

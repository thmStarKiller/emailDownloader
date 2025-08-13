import sys
import os

# Add package directory to path for dependencies
package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'package')
sys.path.insert(0, package_dir)

# Add function directory to path for app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from serverless_wsgi import handle_request
    from app import app
except ImportError as e:
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Import failed: {e}\nPython path: {sys.path}\nDir contents: {os.listdir(".")}'
        }
else:
    def handler(event, context):
        # Strip Netlify function prefix
        path = event.get("path", "/")
        if path.startswith("/.netlify/functions/server"):
            event["path"] = path[len("/.netlify/functions/server"):] or "/"
        
        if "headers" not in event:
            event["headers"] = {}
        
        if "rawPath" in event:
            event["rawPath"] = event["path"]
        
        return handle_request(app, event, context)

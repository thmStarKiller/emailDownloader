import json
import sys
import os

# This is a minimal test function to verify functions work
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Function is working!',
            'path': event.get('path', '/'),
            'python_version': sys.version,
            'cwd': os.getcwd(),
            'dir_contents': os.listdir('.')
        })
    }

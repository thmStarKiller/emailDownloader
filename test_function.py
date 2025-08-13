#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'netlify/functions')

from server import handler

# Test event
event = {
    "path": "/",
    "httpMethod": "GET",
    "headers": {},
    "queryStringParameters": None,
    "body": None
}

context = {}
response = handler(event, context)
print(f"Status: {response.get('statusCode')}")
print(f"Body preview: {response.get('body', '')[:200]}")

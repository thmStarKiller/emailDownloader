def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": "<h1>Test function works!</h1>"
    }

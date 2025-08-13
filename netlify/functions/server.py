def handler(event, context):
    path = event.get("path", "/")
    html = f"""<!DOCTYPE html>
    <html>
    <head><title>SiteSync Pro</title></head>
    <body>
        <h1>SiteSync Pro - Working!</h1>
        <p>Function is working! Path: {path}</p>
        <p><a href="/.netlify/functions/test">Test function</a></p>
    </body>
    </html>"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},  
        "body": html
    }

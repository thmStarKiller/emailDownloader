from app import app
from netlify_wsgi import handler as netlify_handler


def handler(event, context):
    """Netlify entry point for the Flask application."""
    return netlify_handler(app, event, context)

#!/usr/bin/env python3
import os
import sys

print("🚀 Starting SiteSync Pro...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Environment PORT: {os.environ.get('PORT', 'Not set')}")

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import the Flask app from the subdirectory
    print("📦 Importing Flask app...")
    from funny_downloader_app.app import app
    print("✅ Flask app imported successfully")
    
    # Configure app for production
    app.config['DEBUG'] = False
    
    # Expose app for gunicorn
    application = app
    
    # Get port from environment
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Starting server on 0.0.0.0:{port}")
    
    # Start the app (only if running directly, not with gunicorn)
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Available files:")
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

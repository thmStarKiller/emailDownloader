#!/usr/bin/env python3
"""
Manual Git operations since git config is broken
"""
import os
import subprocess
import sys

def run_git_command(cmd):
    """Run git command with proper environment"""
    env = os.environ.copy()
    env['GIT_CONFIG_NOSYSTEM'] = '1'
    env['HOME'] = os.getcwd()
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            env=env,
            cwd=os.getcwd()
        )
        print(f"✅ {cmd}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🔄 Attempting to commit and push to GitHub...")
    
    # Check if files exist
    required_files = [
        'README.md', 'LICENSE', 'Procfile', 'requirements.txt', 
        'funny_downloader_app/app.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing required file: {file}")
            return False
    
    print("✅ All required files present")
    
    # Create a simple script for manual upload
    print("\n📋 Since git is broken, here's what to do:")
    print("1. Go to https://github.com/thmStarKiller/emailDownloader")
    print("2. Click 'Add file' → 'Upload files'")
    print("3. Drag and drop these files:")
    
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in root:
            continue
        for file in files:
            if not file.startswith('.'):
                file_path = os.path.join(root, file).replace('\\', '/')
                if file_path.startswith('./'):
                    file_path = file_path[2:]
                print(f"   - {file_path}")
    
    print("\n4. Commit message: 'Update: Clean SiteSync Pro deployment ready'")
    print("5. Click 'Commit changes'")
    print("\n✅ Then deploy to Railway or Heroku!")

if __name__ == "__main__":
    main()

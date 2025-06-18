import requests
import re
import io
import zipfile
import time
import os
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, make_response

app = Flask(__name__)

# Load Secret Key from Environment Variable
app.secret_key = os.environ.get('SECRET_KEY', 'you-MUST-set-a-real-secret-key')

USERNAME = "storefront"

def extract_page_ids(text):
    ids = []
    id_pattern = re.compile(r"^[A-Z][a-zA-Z0-9]+$")
    ignore_list = {"Email", "Online", "Offline"}
    date_pattern = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
    lines = text.splitlines()
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line: continue
        if date_pattern.match(stripped_line): continue
        if stripped_line in ignore_list: continue
        if id_pattern.match(stripped_line): ids.append(stripped_line)
    return ids

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_files():
    base_url = request.form.get('staging_base_url', '').strip().rstrip('/')
    password = request.form.get('password', '')
    page_ids_text = request.form.get('ids_text', '')
    download_token = request.form.get('downloadToken', '')

    if not base_url or not password or not page_ids_text:
        flash('All fields are required. Please check your input and try again.', 'error')
        return redirect(url_for('index'))

    target_ids = extract_page_ids(page_ids_text)
    if not target_ids:
        flash('No valid Page IDs found in the input. Please ensure IDs start with a capital letter and contain only alphanumeric characters.', 'error')
        return redirect(url_for('index'))

    zip_buffer = io.BytesIO()
    failed_urls = []
    success_count = 0
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for page_id in target_ids:
                url = f"{base_url}/{page_id}.html"
                filename = f"{page_id}.html"
                print(f"Processing: {url}")
                
                try:
                    # Create a session to handle cookies and authentication
                    session = requests.Session()
                    
                    # Add headers that might be required for staging sites
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    session.headers.update(headers)
                    
                    print(f"Attempting to authenticate with username: {USERNAME}")
                    print(f"URL: {url}")
                      # Try multiple authentication methods
                    auth_methods = [
                        (USERNAME, password.strip()),  # Clean password
                        ("admin", password.strip()),
                        ("administrator", password.strip()),
                        ("user", password.strip()),
                        (password.strip(), password.strip()),  # Sometimes username and password are the same
                        ("", password.strip()),  # Empty username
                        # Additional methods for Demandware/Salesforce Commerce Cloud
                        ("demandware", password.strip()),
                        ("sfcc", password.strip()),
                        ("staging", password.strip()),
                        ("test", password.strip()),
                        ("dev", password.strip()),
                    ]
                    
                    response_req = None
                    auth_success = False
                    successful_auth = None
                    
                    for auth_user, auth_pass in auth_methods:
                        print(f"Trying authentication with username: '{auth_user}'")
                        
                        try:
                            response_req = session.get(
                                url, 
                                auth=(auth_user, auth_pass) if auth_user or auth_pass else None,
                                timeout=20,
                                allow_redirects=True
                            )
                            
                            print(f"Response status: {response_req.status_code}")
                            
                            if response_req.status_code == 200:
                                auth_success = True
                                successful_auth = (auth_user, auth_pass)
                                print(f"✓ Authentication successful with username: '{auth_user}'")
                                break
                            elif response_req.status_code == 401:
                                print(f"✗ 401 Unauthorized with username: '{auth_user}'")
                                continue
                            else:
                                print(f"Unexpected status {response_req.status_code} with username: '{auth_user}'")
                                # For some sites, redirects or other status codes might still be success
                                if response_req.status_code in [302, 303, 307, 308]:
                                    print(f"Redirect detected, checking content...")
                                    if len(response_req.content) > 1000:  # Likely got content
                                        auth_success = True
                                        successful_auth = (auth_user, auth_pass)
                                        print(f"✓ Authentication successful with redirect for username: '{auth_user}'")
                                        break
                                
                        except requests.exceptions.RequestException as e:
                            print(f"Request failed with username '{auth_user}': {e}")
                            continue
                    
                    if not auth_success:
                        error_msg = "Authentication failed after trying all methods."
                        if response_req:
                            error_msg += f" Final status: {response_req.status_code}"
                            print(f"Final response headers: {dict(response_req.headers)}")
                            if hasattr(response_req, 'text'):
                                print(f"Final response content preview: {response_req.text[:200]}")
                        else:
                            error_msg += " No response received."
                        raise requests.exceptions.HTTPError(error_msg)
                    
                    # Use the successful response
                    print(f"Using successful authentication: {successful_auth[0]}")
                    response_req.raise_for_status()
                    zipf.writestr(filename, response_req.content)
                    success_count += 1
                    print(f"Successfully processed: {filename}")
                    
                except requests.exceptions.RequestException as e:
                    error_message = f"{e}"
                    if hasattr(e, 'response') and e.response is not None:
                        error_message = f"HTTP {e.response.status_code} - {e}"
                        print(f"Full response content: {e.response.text[:500]}")
                    print(f"Failed to process {url}: {error_message}")
                    failed_urls.append(f"{page_id}.html ({error_message})")
                except Exception as e:
                    print(f"Unexpected error for {url}: {e}")
                    failed_urls.append(f"{page_id}.html (Unexpected Error: {e})")

        if success_count == 0:
            error_list = "; ".join(failed_urls)
            flash(f'Unable to download any files. Errors: {error_list}', 'error')
            return redirect(url_for('index'))

        zip_buffer.seek(0)
        response = make_response(send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'sitesync_content_{int(time.time())}.zip'
        ))
        
        if download_token:
            response.set_cookie('downloadToken', download_token, max_age=60, path='/')
            print(f"Download completion token set: {download_token}")

        # Log results
        if failed_urls:
            print(f'Download completed with warnings: Success={success_count}, Failed={len(failed_urls)}. Failures: {"; ".join(failed_urls)}')
        else:
            print(f'Download completed successfully: {success_count} file(s) processed.')

        return response
        
    except Exception as e:
        print(f"Critical error during processing: {e}")
        flash(f'A system error occurred during processing: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/complete')
def download_complete():
    """Optional completion page for enhanced user experience"""
    return render_template('complete.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

import requests
import re
import io
import zipfile
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, make_response, jsonify

app = Flask(__name__)

# Load Secret Key from Environment Variable
app.secret_key = os.environ.get('SECRET_KEY', 'you-MUST-set-a-real-secret-key')

USERNAME = "storefront"

# Global progress tracking
progress_data = {}

def download_single_file(page_id, base_url, session, auth_methods):
    """Download a single file with authentication attempts - OPTIMIZED"""
    url = f"{base_url}/{page_id}.html"
    filename = f"{page_id}.html"
    
    print(f"⚡ Processing: {filename}")
    
    response_req = None
    auth_success = False
    successful_auth = None
    
    # Try most common auth methods first for speed
    priority_auth = [
        (USERNAME, ""),  # Try empty password first
        (USERNAME, None),  # No auth
        ("admin", ""),
        ("", "")  # No credentials
    ] + auth_methods[:5]  # Limit auth attempts for speed
    
    for auth_user, auth_pass in priority_auth:
        try:
            response_req = session.get(
                url, 
                auth=(auth_user, auth_pass) if auth_user or auth_pass else None,
                timeout=10,  # Reduced timeout for speed
                allow_redirects=True,
                stream=True  # Stream for faster download
            )
            
            if response_req.status_code == 200:
                auth_success = True
                successful_auth = (auth_user, auth_pass)
                print(f"⚡ Fast auth success: {auth_user}")
                break
            elif response_req.status_code in [302, 303, 307, 308]:
                if len(response_req.content) > 500:  # Lower threshold for faster detection
                    auth_success = True
                    successful_auth = (auth_user, auth_pass)
                    print(f"⚡ Redirect auth success: {auth_user}")
                    break
                    
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Quick fail for {auth_user}: {e}")
            continue
    
    if auth_success:
        response_req.raise_for_status()
        return {
            'success': True,
            'filename': filename,
            'content': response_req.content,
            'auth': successful_auth[0],
            'size': len(response_req.content)
        }
    else:
        error_msg = f"Auth failed for {filename}"
        if response_req:
            error_msg += f" (Status: {response_req.status_code})"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'filename': filename,
            'error': error_msg
        }

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

@app.route('/progress/<job_id>')
def get_progress(job_id):
    """Get progress for a specific job"""
    if job_id in progress_data:
        return jsonify(progress_data[job_id])
    return jsonify({'error': 'Job not found'}), 404

@app.route('/start_download', methods=['POST'])
def start_download():
    """Start async download and return job ID"""
    base_url = request.form.get('staging_base_url', '').strip().rstrip('/')
    password = request.form.get('password', '')
    page_ids_text = request.form.get('ids_text', '')
    
    if not base_url or not password or not page_ids_text:
        return jsonify({'error': 'All fields are required'}), 400
    
    target_ids = extract_page_ids(page_ids_text)
    if not target_ids:
        return jsonify({'error': 'No valid Page IDs found'}), 400
    
    # Create job ID
    job_id = f"job_{int(time.time())}_{hash(base_url + password) % 10000}"
    
    # Initialize progress
    progress_data[job_id] = {
        'status': 'starting',
        'progress': 0,
        'total': len(target_ids),
        'completed': 0,
        'failed': 0,
        'current_file': '',
        'funny_message': "🚀 Initializing the interdimensional download portal...",
        'errors': []
    }
    
    # Start download in background thread
    thread = threading.Thread(
        target=process_download_async, 
        args=(job_id, base_url, password, target_ids)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id})

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

def get_funny_messages():
    """Properly vulgar and hilarious Rick & Morty style messages"""
    return [
        "🧪 Rick: 'I'm not gonna sugarcoat it Morty, this download is taking forever because your files are *burp* shit!'",
        "👽 Morty: 'Oh geez Rick, w-w-why does everything have to be so complicated?' Rick: 'Because the universe hates us, Morty!'",
        "� Rick: 'Listen *burp* I've downloaded files across 47 dimensions and yours are still the most fucked up I've seen!'",
        "🤖 Rick: 'These servers are dumber than Jerry trying to use a *burp* smartphone, Morty!'",
        "💀 Rick: 'Your internet connection is slower than Morty's brain, and that's saying something!'",
        "🔬 Rick: 'I'm literally *burp* manipulating quantum packets here while you sit there doing jack shit!'",
        "🍺 Rick: 'I need another drink... this download is more painful than family therapy!'",
        "🌪️ Rick: 'Creating interdimensional portals is easier than downloading your garbage files!'",
        "� Morty: 'Rick, is this legal?' Rick: 'Nothing we do is legal, Morty! That's what makes it fun!'",
        "🍌 Rick: 'I've seen cleaner code in Jerry's browser history, and that's *burp* horrifying!'",
        "� Rick: 'Your files are more scattered than my relationship with your grandmother!'",
        "🦄 Rick: 'Even fictional creatures have better download speeds than this shit!'",
        "🌮 Rick: 'I could cook a five-course meal in the time it takes to download one of your files!'",
        "� Rick: 'This is more of a circus than the time we accidentally *burp* enslaved an entire planet!'",
        "🚂 Rick: 'All aboard the pain train! Next stop: disappointment station!'",
        "🧠 Rick: 'Using 0.03% of my brain capacity and still outsmarting every computer here!'",
        "🎮 Rick: 'I could beat Dark Souls blindfolded faster than this download completes!'",
        "🦆 Rick: 'These rubber duck debuggers have more intelligence than your server architecture!'",
        "🍄 Rick: 'I'm growing mushrooms in the time it takes your files to *burp* process!'",
        "💩 Rick: 'This code is more broken than our family dynamics, Morty!'",
        "🔥 Rick: 'Your server is burning slower than my liver processes alcohol!'",
        "⚡ Rick: 'I've created life itself and it's still easier than fixing your shit code!'",
        "� Rick: 'Missing target files like Jerry misses the point of everything!'",
        "🐍 Rick: 'Python is called Python because it's *burp* slowly strangling your data to death!'",
        "🍕 Rick: 'Ordered pizza, ate pizza, got food poisoning, recovered, and your files are still downloading!'",
        "� Rick: 'I could paint the Mona Lisa with my ass and still finish before this download!'",
        "🚀 Rick: 'Houston, we have a problem: your files are dog shit!'",
        "💸 Rick: 'Wasting more time than Jerry at a job interview!'",
        "� Rick: 'This is taking longer than explaining science to your father!'",
        "🔫 Rick: 'I've killed people for less than making me wait this long, Morty!'",
        "� Rick: 'Getting drunk would be more productive than waiting for this!'",
        "🤡 Rick: 'Your download speed is more of a joke than Jerry's existence!'",
        "� Rick: 'More disappointing than the time Morty tried to *burp* save the universe!'",
        "� Rick: 'Rolling dice would give us better file transfer rates!'",
        "� Rick: 'Even zombies move faster than your data packets!'",
        "🎬 Rick: 'This download is dragging on longer than a Jerry monologue!'",
        "⏰ Rick: 'Time moves slower when you're watching paint dry... or downloading your files!'",
        "🍸 Rick: 'I could distill my own alcohol faster than this processes!'",
        "🚽 Rick: 'Your code belongs in the toilet with the rest of Jerry's ideas!'",
        "� Rick: 'I could terraform a moon in the time this takes to finish!'",
        "🔧 Rick: 'More broken than Morty's confidence after a family dinner!'",
        "🎭 Rick: 'This performance is worse than community theater in dimension C-137!'",
        "💀 Rick: 'I'm dying of old age waiting for your prehistoric download speeds!'",
        "🍆 Rick: 'Your files are processing slower than Jerry trying to understand basic concepts!'",
        "🌈 Rick: 'Creating rainbows from scratch would be faster than this shit show!'",
        "🔮 Rick: 'I predict this will finish sometime after the heat death of the universe!'",
        "⚗️ Rick: 'Brewing illegal chemicals is less *burp* complicated than your file structure!'",
        "� Rick: 'Better odds at a rigged casino than your files downloading correctly!'",
        "🍔 Rick: 'Fast food is slower than your download and that's saying something!'",
        "🎪 Rick: 'Welcome to the circus of incompetence, starring your server infrastructure!'"
    ]

def get_extra_vulgar_messages():
    """Extra vulgar Rick & Morty messages for when users need more entertainment"""
    return [
        "🖕 Rick: 'Fuck this shit, Morty! I could debug reality itself faster than this!'",
        "💀 Rick: 'This download is more fucked than Jerry's life choices!'",
        "🤬 Rick: 'Holy shit, Morty! These files are taking longer than your puberty!'",
        "🍺 Rick: 'I'm getting shitfaced drunk waiting for your ass files to download!'",
        "🔥 Rick: 'This is more of a clusterfuck than our last family vacation!'",
        "💩 Rick: 'Your code is so shitty, it makes Jerry look competent!'",
        "🤯 Rick: 'What the fuck is taking so goddamn long?! I've destroyed civilizations faster!'",
        "🚽 Rick: 'Flushing this shit down the toilet would be more productive!'",
        "⚡ Rick: 'Jesus fucking Christ, Morty! Is this server powered by hamsters?!'",
        "🎪 Rick: 'This shitshow is more entertaining than Jerry's career!'"
    ]

def get_combined_funny_messages():
    """Combine regular and extra vulgar messages for maximum entertainment"""
    regular = get_funny_messages()
    extra = get_extra_vulgar_messages()
    return regular + extra

def process_download_async(job_id, base_url, password, target_ids):
    """Process downloads asynchronously with parallel execution and vulgar Rick humor"""
    funny_messages = get_combined_funny_messages()  # Use combined vulgar messages
    
    try:
        # Update status
        progress_data[job_id]['status'] = 'processing'
        progress_data[job_id]['funny_message'] = funny_messages[0]
        
        # Prepare session and auth methods
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        session.headers.update(headers)
        
        auth_methods = [
            (USERNAME, password.strip()),
            ("admin", password.strip()),
            ("administrator", password.strip()),
            ("user", password.strip()),
            (password.strip(), password.strip()),
            ("", password.strip()),
            ("demandware", password.strip()),
            ("sfcc", password.strip()),
            ("staging", password.strip()),
            ("test", password.strip()),
            ("dev", password.strip()),
        ]
        
        # Create zip buffer
        zip_buffer = io.BytesIO()
        results = []
          # Parallel processing with ThreadPoolExecutor - OPTIMIZED FOR SPEED
        max_workers = min(20, len(target_ids))  # Increased workers for speed
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zipf:  # Fast compression
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all jobs at once for maximum parallelism
                future_to_id = {
                    executor.submit(download_single_file, page_id, base_url, session, auth_methods): page_id 
                    for page_id in target_ids
                }
                
                completed = 0
                message_index = 0
                
                # Process completed downloads as they finish
                for future in as_completed(future_to_id):
                    page_id = future_to_id[future]
                    completed += 1
                    
                    # Update funny message every 2 completions or immediately for first few
                    if completed <= 3 or completed % 2 == 0:
                        message_index = (message_index + 1) % len(funny_messages)
                        progress_data[job_id]['funny_message'] = funny_messages[message_index]
                        print(f"🎭 Updated message: {funny_messages[message_index]}")
                    
                    try:
                        result = future.result(timeout=30)  # 30 second timeout per file
                        results.append(result)
                        
                        if result['success']:
                            zipf.writestr(result['filename'], result['content'])
                            progress_data[job_id]['completed'] += 1
                            print(f"✅ Successfully processed: {result['filename']}")
                        else:
                            progress_data[job_id]['failed'] += 1
                            progress_data[job_id]['errors'].append(result['error'])
                            print(f"❌ Failed: {result['error']}")
                        
                        # Update progress
                        progress_data[job_id]['progress'] = int((completed / len(target_ids)) * 100)
                        progress_data[job_id]['current_file'] = result['filename']
                        
                    except Exception as e:
                        progress_data[job_id]['failed'] += 1
                        progress_data[job_id]['errors'].append(f"Error processing {page_id}: {str(e)}")
                        print(f"❌ Exception for {page_id}: {e}")
        
        # Finalize
        if progress_data[job_id]['completed'] > 0:
            zip_buffer.seek(0)
            progress_data[job_id]['status'] = 'completed'
            progress_data[job_id]['funny_message'] = "🎉 Rick would be proud! Download complete, you magnificent bastard!"
            progress_data[job_id]['zip_data'] = zip_buffer.getvalue()
            progress_data[job_id]['filename'] = f'sitesync_content_{int(time.time())}.zip'
        else:
            progress_data[job_id]['status'] = 'failed'
            progress_data[job_id]['funny_message'] = "💀 Well, this is awkward... Everything failed. Even Rick can't fix this mess."
        
    except Exception as e:
        progress_data[job_id]['status'] = 'failed'
        progress_data[job_id]['funny_message'] = f"🤯 Something went catastrophically wrong: {str(e)}"
        print(f"Critical error in async processing: {e}")

@app.route('/download_result/<job_id>')
def download_result(job_id):
    """Download the completed zip file"""
    if job_id not in progress_data:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = progress_data[job_id]
    
    if job_data['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    if 'zip_data' not in job_data:
        return jsonify({'error': 'No data available'}), 404
    
    zip_buffer = io.BytesIO(job_data['zip_data'])
    
    response = make_response(send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=job_data['filename']
    ))
    
    # Clean up job data after download
    del progress_data[job_id]
    
    return response

# Production configuration
if __name__ == '__main__':
    # Only for local development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

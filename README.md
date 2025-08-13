# SiteSync Pro - Enterprise Content Downloader

A sophisticated web application for downloading HTML pages from password-protected staging environments and packaging them into ZIP files.

## Features

- **Enterprise-grade Authentication** - Supports multiple authentication methods for staging environments
- **Bulk Page Download** - Download multiple HTML pages in one operation
- **Smart Input Processing** - Automatically extracts valid Page IDs from user input
- **Modern UI** - Corporate-styled interface with loading animations and typewriter effects
- **Security-focused** - Built with enterprise security standards in mind

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Modern CSS with glassmorphism effects
- **Fonts**: Inter & JetBrains Mono
- **Authentication**: HTTP Basic Auth with multiple fallbacks

## Getting Started

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/thmStarKiller/emailDownloader.git
cd emailDownloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application (development):
```bash
python app.py
```

Or run the production entrypoint (mirrors Procfile):
```bash
python main.py
```

4. Open your browser to `http://localhost:5000`

### Deployment

### Netlify (Serverless Functions)

This repository now contains a `netlify.toml` and a Python function wrapper (`netlify/functions/server.py`) so the Flask app runs inside a single Netlify Function.

Key points:

1. Build configuration
   - Build command: `pip install -r requirements.txt`
   - Functions directory: `netlify/functions`
   - Publish directory: `static` (only static assets are published directly; all dynamic routes go to the function)
2. Redirect rules
   - All API / Flask routes are rewritten to `/.netlify/functions/server/...` while preserving the trailing path segments.
   - Static assets under `/static/*` are served directly via CDN first for performance.
3. Included files
   - Templates, static assets, font, and `app.py` are bundled via the `included_files` list in `netlify.toml`.
4. Path handling
   - The function handler strips the `/.netlify/functions/server` prefix so Flask receives the real route (`/`, `/start_download`, etc.).

Deploy Steps:
1. Push to GitHub.
2. In Netlify create a new site from the repo.
3. Set build settings (they will auto-detect from `netlify.toml`).
4. Add environment variable `SECRET_KEY` (recommended) under Site Settings → Build & Deploy → Environment.
5. Trigger a deploy.

Limitations (Important):
- The asynchronous multi-poll progress workflow (`/start_download` + `/progress/<job_id>`) relies on in‑memory Python globals. Serverless platforms (including Netlify Functions) do NOT guarantee container reuse between invocations. This means jobs or progress state can disappear mid-process. For reliable async behavior use a persistent host (Railway / Render / Fly.io / Heroku) or add an external store (Redis, DynamoDB, Upstash, etc.).
- Threads spawned inside a function may be frozen or terminated once the handler returns; large parallel downloads can silently stop. For Netlify keep batches small or fall back to the synchronous `/download` endpoint.

Troubleshooting:
- 404 on root: Confirm the catch‑all redirect (the last block) exists in `netlify.toml` and redeploy.
- Function not finding templates: Ensure `app.py`, `templates/`, and `static/` listed under `included_files` (clear cache + redeploy if needed).
- Timeouts: Netlify Functions have hard execution limits (~10–26s depending on plan) — reduce number of pages per batch.
- Progress stuck: Likely a cold container reset; move to persistent hosting or add external state backend.
- Unicode / binary ZIP issues: Already handled by storing ZIP bytes outside the JSON progress object.

### Heroku / Railway (Container Style)

Still supported. A `Procfile` (`web: python main.py`) is provided. For higher concurrency, you can rename `Procfile.gunicorn` to `Procfile` to use Gunicorn.

Environment Variable:
- `SECRET_KEY` – set to a secure random string.

## Usage

1. Enter your staging environment URL (e.g., `https://www-stg-brand-country-ng.dw-sites.com`)
2. Provide the authentication password
3. List the Page IDs you want to download (one per line)
4. Click "Initialize Download Sequence"
5. Watch the sophisticated typewriter loading effect
6. Download your ZIP file when complete

## Authentication

The app automatically tries multiple authentication methods:
- `storefront` (default)
- `admin`, `administrator`, `user`
- `demandware`, `sfcc`, `staging`, `test`, `dev`
- Password as username
- Empty username

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Built with ❤️ for enterprise content management**

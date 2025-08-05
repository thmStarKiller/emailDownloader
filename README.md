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

3. Run the application:
```bash
python app.py
```

4. Open your browser to `http://localhost:5000`

### Deployment

The project includes configuration for deployment on **Netlify** using
serverless functions:

1. Push the repository to GitHub.
2. Create a new Netlify site connected to the repository.
3. Netlify will automatically install the Python dependencies and build
   the serverless function defined in `netlify/functions/server.py`.
4. Set the `SECRET_KEY` environment variable in your Netlify site
   settings.
5. Deploy the site and access it via your Netlify domain.

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

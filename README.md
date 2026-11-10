# Facebook Public Page Video Tool

A small Flask web app that attempts to list publicly accessible Facebook video entries, displays the post text returned by the extractor, downloads individual accessible videos, and exports captions to CSV.

## Run locally
1. Install Python 3.10 or newer.
2. In this folder run:
   `python -m venv .venv`
3. Activate the environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Run: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000`

## Deploy as a website
This project includes a `render.yaml` and `Procfile` for a Python hosting service such as Render. Create a new web service from the project repository and deploy it. A public URL is provided by the hosting service.

## Important limitations
- Facebook does not guarantee anonymous access to all videos or page feeds. Page-wide enumeration may return incomplete results or fail.
- Some URLs require login, are region-limited, removed, age-restricted, or otherwise unavailable. This app does not bypass those controls.
- The caption field is the post text/description returned by the extractor; it is not guaranteed to include every comment or on-screen subtitle.
- For a page you administer, the official Meta Graph API is the more reliable compliant route, but it requires an eligible app, permissions, and access tokens. Public third-party pages may not expose all video data.
- Download only content you own or have permission to save, and comply with Facebook's terms and copyright law.
- This starter app has no user accounts, authentication, rate limiting, or persistent job storage. Add these before production use.

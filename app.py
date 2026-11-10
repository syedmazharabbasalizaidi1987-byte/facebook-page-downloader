import os
import re
import uuid
import csv
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

def valid_facebook_url(url):
    return bool(re.match(r"^https?://(www\.)?(facebook\.com|fb\.watch)/", url.strip(), re.I))

def clean_entry(entry):
    return {
        "id": str(entry.get("id") or ""),
        "title": entry.get("title") or "Facebook video",
        "caption": entry.get("description") or entry.get("title") or "",
        "url": entry.get("webpage_url") or entry.get("url") or "",
        "thumbnail": entry.get("thumbnail") or "",
        "date": entry.get("upload_date") or ""
    }

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/scan")
def scan():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not valid_facebook_url(url):
        return jsonify(error="Please enter a valid Facebook Page or video URL."), 400

    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "playlistend": 200,
        "ignoreerrors": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            return jsonify(error="Facebook did not return video information for this URL."), 422
        entries = info.get("entries") or [info]
        videos = [clean_entry(e) for e in entries if e]
        videos = [v for v in videos if v["url"]]
        return jsonify(videos=videos, note="Results depend on what Facebook makes publicly accessible.")
    except Exception as exc:
        return jsonify(error="Could not read this page. Facebook may require sign-in, block automated access, or not expose a video list. Details: " + str(exc)[:350]), 422

@app.post("/api/download")
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not valid_facebook_url(url):
        return jsonify(error="Invalid Facebook video URL."), 400

    job_dir = tempfile.mkdtemp(prefix="fb_page_tool_")
    output = os.path.join(job_dir, "%(title).80s-%(id)s.%(ext)s")
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "outtmpl": output,
        "format": "best[ext=mp4]/best",
        "merge_output_format": "mp4",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        candidates = [os.path.join(job_dir, f) for f in os.listdir(job_dir) if os.path.isfile(os.path.join(job_dir, f))]
        if not candidates:
            return jsonify(error="No downloadable video was returned."), 422
        path = max(candidates, key=os.path.getsize)
        return send_file(path, as_attachment=True, download_name=os.path.basename(path))
    except Exception as exc:
        return jsonify(error="Download failed. The video may be restricted or unavailable. Details: " + str(exc)[:350]), 422

@app.post("/api/export")
def export():
    data = request.get_json(silent=True) or {}
    videos = data.get("videos") or []
    if not isinstance(videos, list) or not videos:
        return jsonify(error="There are no captions to export."), 400
    job_dir = tempfile.mkdtemp(prefix="fb_captions_")
    path = os.path.join(job_dir, "facebook_captions.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "caption", "date", "video_url"])
        writer.writeheader()
        for v in videos:
            writer.writerow({
                "title": v.get("title", ""),
                "caption": v.get("caption", ""),
                "date": v.get("date", ""),
                "video_url": v.get("url", "")
            })
    return send_file(path, as_attachment=True, download_name="facebook_captions.csv")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

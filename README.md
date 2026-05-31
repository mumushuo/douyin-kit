# Douyin Kit

> Download public videos from Douyin (Chinese TikTok) creators — for personal backup and research use only.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ⚠️ Disclaimer

**This tool is for personal learning and research purposes only.**

- Only downloads **publicly available** videos that are visible without login
- Videos are downloaded **with original watermarks intact** (no watermark removal)
- Do **NOT** use this tool for commercial purposes, copyright infringement, or content redistribution
- Users are solely responsible for complying with Douyin's Terms of Service
- Respect creators' rights — use responsibly

This project is not affiliated with, endorsed by, or associated with Douyin or ByteDance.

---

## Features

- **Browser-based cookie acquisition** — login once via Playwright
- **Bypasses API pagination limits** — scrolls through the creator page to collect ALL videos
- **Date filtering** — download videos from specific date ranges
- **Incremental download** — skip already downloaded videos
- **Metadata export** — save video info as JSON for offline analysis
- **No API keys required** — uses your own browser session

---

## Installation

```bash
# Clone
git clone https://github.com/mumushuo/douyin-kit.git
cd douyin-kit

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

---

## Quick Start

### One-command pipeline

```bash
python main.py all "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31 \
  --output ./downloads/
```

### Step-by-step workflow

**1. Get cookies (first time only)**

```bash
python main.py fetch-cookies
```

A browser window opens. Log in to Douyin, then close the browser. Cookies are saved to `config/cookies.json`.

**2. Scrape video list**

```bash
# Get all videos
python main.py scrape "https://www.douyin.com/user/YOUR_SEC_UID"

# Filter by date
python main.py scrape "https://www.douyin.com/user/YOUR_SEC_UID" \
  --start-date 2026-05-01 \
  --end-date 2026-05-31
```

Output: `videos.json` with full video metadata.

**3. Download videos**

```bash
python main.py download --metadata videos.json --output ./downloads/
```

Each video is saved in its own folder with `.mp4` video, `_cover.jpg` thumbnail, and `_data.json` metadata.

---

## How to Get the Creator URL

1. Open Douyin and visit the creator's profile page
2. Copy the URL from your browser's address bar
3. It looks like: `https://www.douyin.com/user/MS4wLjABAA...`

---

## Directory Structure

```
douyin-kit/
├── main.py                  # CLI entry point
├── douyin_kit/
│   ├── __init__.py
│   ├── cookie_fetcher.py    # Browser login & cookie extraction
│   ├── scraper.py           # Page scrolling & metadata collection
│   └── downloader.py        # Video download with aiohttp
├── config/
│   └── cookies.json         # Generated after fetch-cookies
├── videos.json              # Generated after scrape
├── downloads/               # Downloaded videos
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Requirements

- Python 3.10+
- Playwright (Chromium)
- aiohttp

---

## License

MIT © [mumushuo](https://github.com/mumushuo)

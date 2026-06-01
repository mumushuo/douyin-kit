#!/usr/bin/env python3
"""Douyin Kit - Download public videos from Douyin creators.

Workflow:
  1. fetch-cookies  - Login via browser and save cookies
  2. scrape         - Scroll creator page and collect video metadata
  3. download       - Download videos from scraped metadata
  4. all-in-one     - Run the full pipeline

For personal backup and research use only.
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from douyin_kit.cookie_fetcher import capture_cookies
from douyin_kit.scraper import DouyinScraper
from douyin_kit.downloader import download_videos


def cmd_fetch_cookies(args):
    """Step 1: Acquire Douyin cookies."""
    asyncio.run(capture_cookies(args.url, args.output, args.headless))


def cmd_scrape(args):
    """Step 2: Scrape video list from creator page."""
    cookies = DouyinScraper._load_cookies(args.cookies) if args.cookies.exists() else []
    scraper = DouyinScraper(cookies)

    start = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    end = datetime.strptime(args.end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59) if args.end_date else None

    results = asyncio.run(scraper.scrape(args.url, start, end, args.headless))

    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] Saved {len(results)} videos to {args.output}")


def cmd_download(args):
    """Step 3: Download videos from metadata."""
    awemes = json.loads(args.metadata.read_text(encoding="utf-8"))
    asyncio.run(download_videos(awemes, args.output, skip_existing=not args.no_skip, mode=args.mode))


def cmd_all(args):
    """Run all steps: login -> scrape -> download."""
    # Step 1: Check cookies
    cookies_path = args.cookies
    if not cookies_path.exists():
        print("[STEP 1/3] Fetching cookies...")
        asyncio.run(capture_cookies("https://www.douyin.com/", cookies_path))
    else:
        print("[STEP 1/3] Using existing cookies from", cookies_path)

    # Step 2: Scrape
    print(f"[STEP 2/3] Scraping videos from {args.url}...")
    cookies = DouyinScraper._load_cookies(cookies_path) if cookies_path.exists() else []
    scraper = DouyinScraper(cookies)

    start = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    end = datetime.strptime(args.end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59) if args.end_date else None
    awemes = asyncio.run(scraper.scrape(args.url, start, end, args.headless))

    if not awemes:
        print("[ERROR] No videos found. Exiting.")
        return

    # Step 3: Download
    print(f"[STEP 3/3] Downloading {len(awemes)} videos to {args.output}...")
    asyncio.run(download_videos(awemes, args.output, mode=args.mode))


def main():
    parser = argparse.ArgumentParser(
        description="Douyin Kit - Download public videos from Douyin creators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Step 1: Login and save cookies
  python main.py fetch-cookies

  # Step 2: Scrape all videos from a creator
  python main.py scrape "https://www.douyin.com/user/SEC_UID"

  # Step 2: Scrape videos from May 2026
  python main.py scrape "https://www.douyin.com/user/SEC_UID" --start-date 2026-05-01 --end-date 2026-05-31

  # Step 3: Download scraped videos
  python main.py download --metadata videos.json --output ./downloads/

  # All-in-one pipeline
  python main.py all "https://www.douyin.com/user/SEC_UID" \
    --start-date 2026-05-01 --end-date 2026-05-31 \
    --output ./downloads/
""",
    )

    sub = parser.add_subparsers(dest="command", help="Sub-commands")

    # fetch-cookies
    p1 = sub.add_parser("fetch-cookies", help="Login via browser and save cookies")
    p1.add_argument("--url", default="https://www.douyin.com/", help="Login page URL")
    p1.add_argument("--output", type=Path, default=Path("config/cookies.json"), help="Cookies output file")
    p1.add_argument("--headless", action="store_true", help="Run headless")
    p1.set_defaults(func=cmd_fetch_cookies)

    # scrape
    p2 = sub.add_parser("scrape", help="Scrape video list")
    p2.add_argument("url", help="Creator profile URL")
    p2.add_argument("--cookies", type=Path, default=Path("config/cookies.json"), help="Cookies file")
    p2.add_argument("--start-date", help="Start date filter (YYYY-MM-DD)")
    p2.add_argument("--end-date", help="End date filter (YYYY-MM-DD)")
    p2.add_argument("--headless", action="store_true", help="Headless mode")
    p2.add_argument("--output", type=Path, default=Path("videos.json"), help="Output JSON")
    p2.set_defaults(func=cmd_scrape)

    # download
    p3 = sub.add_parser("download", help="Download videos from metadata")
    p3.add_argument("--metadata", type=Path, required=True, help="Path to videos.json")
    p3.add_argument("--output", type=Path, default=Path("downloads"), help="Output directory")
    p3.add_argument("--no-skip", action="store_true", help="Don't skip existing")
    p3.add_argument("--mode", choices=["folder", "video-only"], default="folder",
                    help="Download mode: folder (default, including cover+metadata) or video-only")
    p3.set_defaults(func=cmd_download)

    # all-in-one
    p4 = sub.add_parser("all", help="Full pipeline: login -> scrape -> download")
    p4.add_argument("url", help="Creator profile URL")
    p4.add_argument("--cookies", type=Path, default=Path("config/cookies.json"), help="Cookies file")
    p4.add_argument("--start-date", help="Start date filter (YYYY-MM-DD)")
    p4.add_argument("--end-date", help="End date filter (YYYY-MM-DD)")
    p4.add_argument("--headless", action="store_true", help="Headless mode")
    p4.add_argument("--output", type=Path, default=Path("downloads"), help="Output directory")
    p4.add_argument("--mode", choices=["folder", "video-only"], default="folder",
                    help="Download mode: folder (default, including cover+metadata) or video-only")
    p4.set_defaults(func=cmd_all)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()

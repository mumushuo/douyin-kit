"""Video downloader using signed URLs from scraped metadata.

Two download modes:
  - "folder": video + cover + metadata in sub-directories (default)
  - "video-only": only .mp4 files, flat in output directory
"""
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

import aiohttp


def sanitize_filename(name: str) -> str:
    """Remove illegal filename characters."""
    return re.sub(r'[\\/:*?"<>|]', '_', name)[:80]


async def download_file(
    session: aiohttp.ClientSession,
    url: str,
    dest: Path,
    headers: dict,
    label: str = "",
) -> bool:
    """Download a single file."""
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            if resp.status == 200:
                dest.write_bytes(await resp.read())
                print(f"  [OK] {label or dest.name} ({dest.stat().st_size} bytes)")
                return True
            elif resp.status == 302:
                redirect = resp.headers.get("Location", "")
                if redirect:
                    async with session.get(redirect, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as resp2:
                        if resp2.status == 200:
                            dest.write_bytes(await resp2.read())
                            print(f"  [OK] {label or dest.name} via redirect ({dest.stat().st_size} bytes)")
                            return True
                        print(f"  [FAIL] {label} redirect HTTP {resp2.status}")
            else:
                print(f"  [FAIL] {label} HTTP {resp.status}")
    except Exception as e:
        print(f"  [ERR] {label}: {e}")
    return False


async def download_videos(
    awemes: list[dict],
    output_dir: Path,
    cookies: dict | None = None,
    skip_existing: bool = True,
    mode: str = "folder",
) -> dict:
    """Download videos from scraped aweme metadata.

    Args:
        awemes: List of aweme dicts from scraper
        output_dir: Directory to save downloads
        cookies: Optional cookies dict for download requests
        skip_existing: Skip already-downloaded videos
        mode: "folder" (default) -- video + cover + metadata in sub-directories
              "video-only" -- only .mp4 files, saved flat in output_dir

    Returns:
        Stats dict: {total, success, skipped, failed}
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = {"total": len(awemes), "success": 0, "skipped": 0, "failed": 0}

    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    headers = {
        "User-Agent": ua,
        "Referer": "https://www.douyin.com/",
    }

    async with aiohttp.ClientSession() as session:
        for i, aweme in enumerate(awemes):
            aweme_id = str(aweme.get("aweme_id", ""))
            desc = aweme.get("desc", "no_title")
            create_time = aweme.get("create_time", 0)
            dt = datetime.fromtimestamp(create_time)
            date_str = dt.strftime("%Y-%m-%d")

            safe_desc = sanitize_filename(desc)
            folder_name = f"{date_str}_{safe_desc}_{aweme_id}"

            if mode == "video-only":
                # Flat mode: just the .mp4 file
                video_file = output_dir / f"{folder_name}.mp4"
                if skip_existing and video_file.exists():
                    print(f"\n[{i+1}/{len(awemes)}] SKIP (exists): {folder_name[:60]}")
                    stats["skipped"] += 1
                    continue
            else:
                # Folder mode: sub-directory with video + cover + metadata
                video_dir = output_dir / folder_name
                if skip_existing and video_dir.exists():
                    mp4_files = list(video_dir.glob("*.mp4"))
                    if mp4_files:
                        print(f"\n[{i+1}/{len(awemes)}] SKIP (exists): {folder_name[:60]}")
                        stats["skipped"] += 1
                        continue

            print(f"\n[{i+1}/{len(awemes)}] {folder_name[:60]}")

            # Get video URL
            video = aweme.get("video", {})
            play_addr = video.get("play_addr", {})
            url_list = play_addr.get("url_list", [])

            # Fallback to bit_rate list
            if not url_list:
                bit_rates = video.get("bit_rate", [])
                if bit_rates:
                    best = max(bit_rates, key=lambda b: b.get("bit_rate", 0))
                    url_list = best.get("play_addr", {}).get("url_list", [])

            if not url_list:
                print(f"  [SKIP] No video URL found")
                stats["failed"] += 1
                continue

            video_url = url_list[0]
            # Normalize domain
            video_url = re.sub(r'https?://[^/]+', 'https://www.douyin.com', video_url)

            if mode == "video-only":
                # Download video file only, flat output
                video_path = output_dir / f"{folder_name}.mp4"
                success = await download_file(session, video_url, video_path, headers, "video")
                if not success:
                    stats["failed"] += 1
                    continue
            else:
                # Folder mode: create sub-directory
                video_dir = output_dir / folder_name
                video_dir.mkdir(parents=True, exist_ok=True)

                video_path = video_dir / f"{folder_name}.mp4"
                success = await download_file(session, video_url, video_path, headers, "video")
                if not success:
                    stats["failed"] += 1
                    continue

                # Download cover
                cover = video.get("cover", {})
                cover_urls = cover.get("url_list", [])
                if cover_urls:
                    cover_path = video_dir / f"{folder_name}_cover.jpg"
                    await download_file(session, cover_urls[0], cover_path, headers, "cover")

                # Save metadata
                meta_path = video_dir / f"{folder_name}_data.json"
                meta_path.write_text(json.dumps(aweme, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  [OK] metadata")

            stats["success"] += 1
            await asyncio.sleep(1)

    print(f"\n[DONE] Total: {stats['total']} | Success: {stats['success']} | Skipped: {stats['skipped']} | Failed: {stats['failed']}")
    return stats


def main():
    """CLI entry point for downloading."""
    import argparse

    parser = argparse.ArgumentParser(description="Download videos from scraped metadata")
    parser.add_argument("--metadata", type=Path, required=True, help="Path to videos.json from scraper")
    parser.add_argument("--output", type=Path, default=Path("downloads"), help="Output directory")
    parser.add_argument("--no-skip", action="store_true", help="Don't skip existing downloads")
    parser.add_argument("--mode", choices=["folder", "video-only"], default="folder",
                        help="Download mode: folder (default) or video-only")
    args = parser.parse_args()

    awemes = json.loads(args.metadata.read_text(encoding="utf-8"))
    asyncio.run(download_videos(awemes, args.output, skip_existing=not args.no_skip, mode=args.mode))


if __name__ == "__main__":
    main()

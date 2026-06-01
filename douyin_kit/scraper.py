"""Video listing scraper using Playwright to bypass API pagination limits."""
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class DouyinScraper:
    """Scroll through a Douyin creator page and collect video metadata."""

    def __init__(self, cookies: list[dict] | None = None):
        self.cookies = cookies or []
        self.results: list[dict] = []

    @staticmethod
    def _load_cookies(path: Path) -> list[dict]:
        """Load cookies from JSON file (dict or list format)."""
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return [
                {"name": k, "value": str(v), "domain": ".douyin.com", "path": "/"}
                for k, v in raw.items()
            ]
        return raw if isinstance(raw, list) else []

    async def scrape(
        self,
        user_url: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        headless: bool = False,
        max_scrolls: int = 200,
    ) -> list[dict]:
        """Scrape all public videos from a creator page.

        Args:
            user_url: Creator profile URL (e.g., https://www.douyin.com/user/SEC_UID)
            start_date: Optional filter: only videos on or after this date
            end_date: Optional filter: only videos on or before this date
            headless: Run browser without GUI
            max_scrolls: Maximum scroll operations

        Returns:
            List of aweme (video) metadata dicts
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("playwright is required. Run: pip install playwright && playwright install chromium")

        seen_ids: set[str] = set()
        captured: list[dict] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                locale="zh-CN",
                viewport={"width": 1600, "height": 900},
            )
            if self.cookies:
                await context.add_cookies(self.cookies)

            page = await context.new_page()
            responses: list[dict] = []

            async def on_response(response):
                url = response.url or ""
                if "/aweme/v1/web/aweme/post/" in url:
                    try:
                        data = await response.json()
                        responses.append(data)
                    except Exception:
                        pass

            page.on("response", on_response)

            print(f"[INFO] Opening {user_url}")
            await page.goto(user_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)

            prev_count = 0
            stall_rounds = 0

            for i in range(max_scrolls):
                new_count = 0
                for resp in responses:
                    for item in resp.get("aweme_list", []):
                        aid = str(item.get("aweme_id", ""))
                        if aid and aid not in seen_ids:
                            seen_ids.add(aid)
                            captured.append(item)
                            new_count += 1

                if i % 10 == 0:
                    print(f"[SCROLL {i}] Videos found: {len(captured)}")

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

                # Check for end-of-feed indicator
                no_more = await page.evaluate("""() => {
                    const spans = document.querySelectorAll('span');
                    for (const s of spans) {
                        if (s.textContent && s.textContent.includes('没有更多了')) return true;
                    }
                    return false;
                }""")
                if no_more:
                    print("[INFO] End of feed reached.")
                    break

                current = len(captured)
                if current == prev_count:
                    stall_rounds += 1
                    if stall_rounds >= 5:
                        print("[INFO] No new videos, stopping scroll.")
                        break
                else:
                    stall_rounds = 0
                prev_count = current

            # Final capture
            for resp in responses:
                for item in resp.get("aweme_list", []):
                    aid = str(item.get("aweme_id", ""))
                    if aid and aid not in seen_ids:
                        seen_ids.add(aid)
                        captured.append(item)

            await browser.close()

        print(f"[INFO] Total videos captured: {len(captured)}")

        # Date filtering
        if start_date or end_date:
            filtered = []
            for item in captured:
                ts = item.get("create_time", 0)
                dt = datetime.fromtimestamp(ts)
                if start_date and dt < start_date:
                    continue
                if end_date and dt > end_date:
                    continue
                filtered.append(item)
            captured = filtered
            print(f"[INFO] After date filter: {len(captured)}")

        self.results = captured
        return captured


def main():
    """CLI entry point for scraping."""
    import argparse

    parser = argparse.ArgumentParser(description="Scrape video list from a Douyin creator")
    parser.add_argument("url", help="Creator profile URL")
    parser.add_argument("--cookies", type=Path, default=Path("config/cookies.json"), help="Cookies file")
    parser.add_argument("--start-date", help="Start date filter (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date filter (YYYY-MM-DD)")
    parser.add_argument("--headless", action="store_true", help="Headless mode")
    parser.add_argument("--output", type=Path, default=Path("videos.json"), help="Output JSON file")
    args = parser.parse_args()

    cookies = DouyinScraper._load_cookies(args.cookies) if args.cookies.exists() else []
    scraper = DouyinScraper(cookies)

    start = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    end = datetime.strptime(args.end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59) if args.end_date else None

    results = asyncio.run(scraper.scrape(args.url, start, end, args.headless))

    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[INFO] Saved {len(results)} videos to {args.output}")


if __name__ == "__main__":
    main()

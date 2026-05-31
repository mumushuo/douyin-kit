"""Cookie acquisition via Playwright browser automation."""
import asyncio
import json
from pathlib import Path
from typing import Any


def sanitize_cookies(cookies: dict) -> dict:
    """Clean and deduplicate cookies."""
    result = {}
    for k, v in cookies.items():
        if v is not None and str(v).strip():
            result[k] = str(v).strip()
    return result


def filter_cookies(cookies: dict) -> dict:
    """Filter to recommended cookie subset for Douyin API access."""
    keys = {
        "msToken", "ttwid", "odin_tt", "passport_csrf_token",
        "sid_guard", "sessionid", "sid_tt", "uid_tt",
        "_waftokenid", "s_v_web_id", "__ac_nonce", "__ac_signature",
        "UIFID", "UIFID_TEMP", "d_ticket", "x-web-secsdk-uid",
        "bd_ticket_guard_client_web_domain", "bd_ticket_guard_web_domain",
        "_bd_ticket_crypt_cookie", "__security_server_data_status",
    }
    picked = {}
    for k, v in cookies.items():
        if k in keys or k.startswith(("__security_mc_", "bd_ticket_guard_", "_bd_ticket_crypt_")):
            picked[k] = v
    return picked or cookies


async def capture_cookies(
    url: str = "https://www.douyin.com/",
    output: Path = Path("config/cookies.json"),
    headless: bool = False,
) -> dict:
    """Launch browser, wait for login, extract and save cookies.

    Args:
        url: Page to open for login
        output: Path to save cookies JSON
        headless: Run browser in headless mode (not recommended)

    Returns:
        Extracted cookies dict
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError("playwright is required. Run: pip install playwright && playwright install chromium")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="zh-CN",
        )
        page = await context.new_page()

        closed = asyncio.Event()

        def _on_close(_page: Any) -> None:
            closed.set()

        page.on("close", _on_close)

        # Navigate in background while waiting
        nav_task = asyncio.create_task(page.goto(url, wait_until="domcontentloaded", timeout=300_000))

        print("[INFO] Browser opened. Please log in to Douyin.")
        print("[INFO] Close the browser window when you see the homepage (logged in).")

        try:
            await asyncio.wait_for(closed.wait(), timeout=300)
            print("[INFO] Browser closed, extracting cookies...")
        except asyncio.TimeoutError:
            print("[INFO] Timeout (5 min), extracting cookies anyway...")
        finally:
            page.remove_listener("close", _on_close)

        if not nav_task.done():
            nav_task.cancel()
            try:
                await nav_task
            except asyncio.CancelledError:
                pass

        storage = await context.storage_state()
        raw_cookies = {
            c["name"]: c["value"]
            for c in storage.get("cookies", [])
            if c.get("domain", "").endswith("douyin.com")
        }
        await context.close()
        await browser.close()

    cookies = sanitize_cookies(raw_cookies)
    cookies = filter_cookies(cookies)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(cookies, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[INFO] Saved {len(cookies)} cookies to {output.resolve()}")

    required = {"msToken", "ttwid", "odin_tt", "passport_csrf_token"}
    missing = required - cookies.keys()
    if missing:
        print(f"[WARN] Missing recommended cookies: {', '.join(missing)}")

    return cookies


def main():
    """CLI entry point for cookie fetching."""
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Douyin cookies via browser login")
    parser.add_argument("--url", default="https://www.douyin.com/", help="Login page URL")
    parser.add_argument("--output", type=Path, default=Path("config/cookies.json"), help="Output file")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    args = parser.parse_args()

    asyncio.run(capture_cookies(args.url, args.output, args.headless))


if __name__ == "__main__":
    main()

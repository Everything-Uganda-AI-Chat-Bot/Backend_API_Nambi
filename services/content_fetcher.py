"""
Content Fetcher — crawls the entire everythinguganda.com site
starting from the homepage and following all internal links.
"""

import os
import concurrent.futures
from urllib.parse import urlparse, urljoin

START_URL = "https://www.everythinguganda.com/"
DOMAIN = "www.everythinguganda.com"
MAX_PAGES = 100  # safety cap


def fetch_full_site(start_url=START_URL):
    print(f"Starting full site crawl from {start_url}")
    result = _playwright_crawl(start_url)
    if result and len(result) > 1000:
        print(f"Crawl complete: {len(result):,} chars")
        return result
    print(f"Crawl got {len(result) if result else 0} chars")
    return result or ""


def _playwright_crawl(start_url):
    """Crawl entire site in a dedicated thread — Linux/Windows safe."""
    def run():
        import asyncio
        try:
            loop = asyncio.ProactorEventLoop()
        except AttributeError:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_crawl_async(start_url))
        finally:
            loop.close()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(run).result(timeout=600)
    except Exception as e:
        print(f"Crawl error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def _crawl_async(start_url):
    from playwright.async_api import async_playwright
    from collections import deque

    visited = set()
    queue = deque([start_url])
    all_text = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--no-first-run",
            ]
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True,
        )

        while queue and len(visited) < MAX_PAGES:
            url = queue.popleft()

            # Normalise URL — strip fragments and query strings for dedup
            parsed = urlparse(url)
            clean = parsed._replace(fragment="").geturl()

            if clean in visited:
                continue
            if parsed.netloc and parsed.netloc != DOMAIN:
                continue  # skip external links

            visited.add(clean)
            page = None

            try:
                print(f"Crawling ({len(visited)}/{MAX_PAGES}): {url}")
                page = await context.new_page()
                await page.goto(url, timeout=60000, wait_until="load")
                await page.wait_for_timeout(3000)  # wait for React

                # Extract text
                content = await page.evaluate("""() => {
                    ['script','style','noscript','nav','footer',
                     'header','iframe','svg'].forEach(t => {
                        document.querySelectorAll(t).forEach(e => e.remove());
                    });
                    return document.body.innerText;
                }""")

                # Collect internal links for crawling
                links = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a[href]'))
                        .map(a => a.href)
                        .filter(h => h.startsWith('http'));
                }""")

                await page.close()

                if content and len(content) > 100:
                    all_text.append(f"\n--- CONTENT FROM {url} ---\n{content}")
                    print(f"  Got {len(content):,} chars")

                # Queue new internal links
                for link in links:
                    p2 = urlparse(link)
                    clean_link = p2._replace(fragment="").geturl()
                    if (p2.netloc == DOMAIN and
                            clean_link not in visited and
                            clean_link not in queue):
                        queue.append(clean_link)

            except Exception as e:
                print(f"  Failed {url}: {e}")
                if page:
                    try:
                        await page.close()
                    except Exception:
                        pass

        await browser.close()

    if not all_text:
        return None

    result = "\n".join(all_text)
    print(f"Crawled {len(visited)} pages, {len(result):,} total chars")
    return result


# Legacy compatibility
def fetch_page(url):
    return _playwright_crawl(url) or ""

def fetch_multiple_pages(urls):
    return _playwright_crawl(urls[0]) or "" if urls else ""

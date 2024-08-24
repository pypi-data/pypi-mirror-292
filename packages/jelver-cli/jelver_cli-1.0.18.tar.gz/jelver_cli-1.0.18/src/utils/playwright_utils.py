""" Utility functions for Playwright """

import math
import os

import asyncio
from io import BytesIO
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright


async def create_context_and_page(
        use_existing_instance=False,
        in_container=False,
        headless=True):
    """
    Create a new browser instance or use an existing user data directory.
    """
    # pylint: disable=too-many-branches
    profile_path = None

    if use_existing_instance:
        if in_container:
            # In Docker, we'll mount the Chrome/Chromium profile directory to /profiles
            profile_path = Path('/profiles')
            if not profile_path.exists():
                raise RuntimeError(
                    'No Chrome or Chromium profile directory mounted at /profiles'
                )
        else:
            if os.name == 'nt':  # Windows
                chrome_path = Path(os.getenv('LOCALAPPDATA')) / 'Google' / 'Chrome' / 'User Data'
                chromium_path = Path(os.getenv('LOCALAPPDATA')) / 'Chromium' / 'User Data'
            elif os.name == 'posix':  # Linux and macOS
                if 'darwin' in os.uname().sysname.lower():  # macOS
                    chrome_path = (
                        Path.home() / 'Library' / 'Application Support' / 'Google' / 'Chrome'
                    )
                    chromium_path = Path.home() / 'Library' / 'Application Support' / 'Chromium'
                else:  # Linux
                    chrome_path = Path.home() / '.config' / 'google-chrome'
                    chromium_path = Path.home() / '.config' / 'chromium'
            else:
                raise RuntimeError('Unsupported OS: os.name')

            if chrome_path.exists():
                profile_path = chrome_path
            elif chromium_path.exists():
                profile_path = chromium_path
            else:
                raise RuntimeError('No Chrome or Chromium profile found')

    args = []
    if in_container:
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--single-process'
        ]

    playwright = await async_playwright().start()
    browser_launcher = playwright.chromium

    if use_existing_instance and profile_path:
        context = await browser_launcher.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            args=args
        )
    else:
        browser = await browser_launcher.launch(
            headless=headless,
            args=args
        )
        context = await browser.new_context()

    page = context.pages[0] if context.pages else await context.new_page()
    return context, page


async def goto_url_with_timeout(page, url, timeout_ms=5000):
    """
    Go to the page and do not wait longer than the timeout.
    """
    try:
        await asyncio.wait_for(
            page.goto(url, wait_until="networkidle"),
            timeout_ms / 1000
        )
    except asyncio.TimeoutError:
        pass
    return page


async def fetch_html_and_screenshots(
        page,
        max_page_size_bytes=1048576,
        max_num_screenshots=None):
    """
    Fetch the HTML and screenshots from the provided page.
    """
    html_task = fetch_page_content(page, max_page_size_bytes)
    screenshots_task = capture_screenshots(
        page,
        max_num_screenshots
    )

    html_result, screenshots_result = await asyncio.gather(
        html_task, screenshots_task
    )

    if isinstance(html_result, Exception):
        raise html_result

    if isinstance(screenshots_result, Exception):
        raise screenshots_result

    return html_result, screenshots_result


async def fetch_page_content(page, max_page_size_bytes):
    """
    Fetch the page content and ensure it does not exceed the max page size.
    """
    content = await page.content()
    if len(content.encode('utf-8')) > max_page_size_bytes:
        raise RuntimeError("Page size exceeds the maximum limit")
    return content


async def capture_screenshots(page, max_num_screenshots=4):
    """
    Capture screenshots of the entire page and convert them to Pillow Images.

    The max_num_screenshots is requires as some website have infinite scrolling.
    """
    # Get the dimensions of the viewport and the full page
    viewport_height = await page.evaluate('window.innerHeight')
    full_page_height = await page.evaluate('document.body.scrollHeight')

    screenshots = []
    num_screenshots = math.ceil(full_page_height / viewport_height)

    for i in range(num_screenshots):
        if max_num_screenshots and i > max_num_screenshots:
            break

        # Scroll to the correct position
        await page.evaluate(f'window.scrollTo(0, {i * viewport_height})')

        # Capture the screenshot
        screenshot_bytes = await page.screenshot()
        screenshots.append(Image.open(BytesIO(screenshot_bytes)))

    return screenshots

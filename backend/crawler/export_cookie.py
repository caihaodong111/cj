# -*- coding: utf-8 -*-

import argparse
import asyncio
import io
import os
import sys
from pathlib import Path
from typing import Optional


CRAWLER_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = CRAWLER_ROOT.parent
os.chdir(CRAWLER_ROOT)
if str(CRAWLER_ROOT) not in sys.path:
    sys.path.insert(0, str(CRAWLER_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

if sys.stdout and hasattr(sys.stdout, "buffer"):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "buffer"):
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv

    env_path = BACKEND_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    pass

os.environ.setdefault("MEDIACRAWLER_QR_MODE", "web")

import config
from playwright.async_api import async_playwright
from tools import utils


PLATFORM_COOKIE_KEYS = {
    "xhs": ("web_session",),
    "dy": ("LOGIN_STATUS", "passport_csrf_token"),
    "ks": ("passToken",),
    "bili": ("SESSDATA", "DedeUserID"),
    "wb": ("SSOLoginState", "WBPSESS"),
    "tieba": ("STOKEN", "PTOKEN", "BDUSS"),
    "zhihu": ("z_c0", "d_c0"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open a platform login page and export the resulting cookie string.")
    parser.add_argument("--platform", required=True, choices=sorted(PLATFORM_COOKIE_KEYS.keys()))
    parser.add_argument("--save", action="store_true", help="Save the exported cookie into CookieConfig.")
    parser.add_argument("--name", default="扫码登录导出", help="CookieConfig name when --save is used.")
    parser.add_argument("--remark", default="", help="CookieConfig remark when --save is used.")
    parser.add_argument("--no-cdp", action="store_true", help="Use standard Playwright instead of CDP mode.")
    return parser.parse_args()


def configure_runtime(platform: str, use_cdp: bool) -> None:
    config.PLATFORM = platform
    config.LOGIN_TYPE = "qrcode"
    config.COOKIES = ""
    config.ENABLE_CDP_MODE = use_cdp
    config.HEADLESS = False
    config.CDP_HEADLESS = False


def load_platform_components(platform: str):
    if platform == "xhs":
        from media_platform.xhs import XiaoHongShuCrawler as Crawler
        from media_platform.xhs.login import XiaoHongShuLogin as Login

        return Crawler, Login
    if platform == "dy":
        from media_platform.douyin import DouYinCrawler as Crawler
        from media_platform.douyin.login import DouYinLogin as Login

        return Crawler, Login
    if platform == "ks":
        from media_platform.kuaishou import KuaishouCrawler as Crawler
        from media_platform.kuaishou.login import KuaishouLogin as Login

        return Crawler, Login
    if platform == "bili":
        from media_platform.bilibili import BilibiliCrawler as Crawler
        from media_platform.bilibili.login import BilibiliLogin as Login

        return Crawler, Login
    if platform == "wb":
        from media_platform.weibo import WeiboCrawler as Crawler
        from media_platform.weibo.login import WeiboLogin as Login

        return Crawler, Login
    if platform == "tieba":
        from media_platform.tieba.core import TieBaCrawler as Crawler
        from media_platform.tieba.login import BaiduTieBaLogin as Login

        return Crawler, Login
    if platform == "zhihu":
        from media_platform.zhihu.core import ZhihuCrawler as Crawler
        from media_platform.zhihu.login import ZhiHuLogin as Login

        return Crawler, Login
    raise ValueError(f"Unsupported platform: {platform}")


async def prepare_page(platform: str, crawler, browser_context):
    if platform == "tieba":
        await crawler._inject_anti_detection_scripts()
        page = await browser_context.new_page()
        crawler.context_page = page
        await crawler._navigate_to_tieba_via_baidu()
        return page

    page = await browser_context.new_page()
    crawler.context_page = page

    if platform == "ks":
        await page.goto(f"{crawler.index_url}?isHome=1")
    elif platform in {"xhs", "dy", "zhihu"}:
        await page.goto(crawler.index_url, wait_until="domcontentloaded")
    else:
        await page.goto(crawler.index_url)

    if platform == "weibo":
        await asyncio.sleep(2)

    return page


async def export_cookie_string(platform: str, browser_context) -> str:
    cookies = None
    if platform == "wb":
        cookies = await browser_context.cookies(urls=["https://m.weibo.cn"])
    else:
        cookies = await browser_context.cookies()
    cookie_str, _ = utils.convert_cookies(cookies)
    return cookie_str


async def verify_existing_session(platform: str, crawler, browser_context) -> bool:
    try:
        if platform == "xhs":
            client = await crawler.create_xhs_client(None)
            return await client.pong()
        if platform == "dy":
            client = await crawler.create_douyin_client(None)
            return await client.pong(browser_context=browser_context)
        if platform == "ks":
            client = await crawler.create_ks_client(None)
            return await client.pong()
        if platform == "bili":
            client = await crawler.create_bilibili_client(None)
            return await client.pong()
        if platform == "wb":
            client = await crawler.create_weibo_client(None)
            return await client.pong()
        if platform == "tieba":
            client = await crawler.create_tieba_client(None, None)
            return await client.pong(browser_context=browser_context)
        if platform == "zhihu":
            client = await crawler.create_zhihu_client(None)
            return await client.pong()
    except Exception as exc:
        print(f"[export_cookie] Existing session verification failed for platform={platform}: {exc}")
        return False
    return False


async def has_login_cookie(platform: str, browser_context) -> bool:
    cookies = await browser_context.cookies()
    _, cookie_dict = utils.convert_cookies(cookies)
    return any(cookie_dict.get(key) for key in PLATFORM_COOKIE_KEYS[platform])


async def post_login_prepare(platform: str, crawler, page, browser_context) -> None:
    if platform == "wb":
        await page.goto(crawler.mobile_index_url)
        await asyncio.sleep(3)
        return
    if platform == "zhihu":
        await page.goto(
            f"{crawler.index_url}/search?q=python&search_source=Guess&utm_content=search_hot&type=content"
        )
        await asyncio.sleep(5)


def save_cookie(platform: str, cookie_str: str, name: str, remark: str) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mediacrawler_config.settings")

    if str(BACKEND_ROOT) in sys.path:
        sys.path.remove(str(BACKEND_ROOT))
    sys.path.insert(0, str(BACKEND_ROOT))

    for module_name in list(sys.modules):
        if module_name == "media_platform" or module_name.startswith("media_platform."):
            sys.modules.pop(module_name, None)

    import django

    django.setup()

    from django.utils import timezone

    from api.models import CookieConfig

    CookieConfig.objects.filter(platform=platform, is_active=True).update(is_active=False)
    existing = CookieConfig.objects.filter(platform=platform, name=name).order_by("-id").first()
    now = timezone.now()
    if existing:
        existing.cookies = cookie_str
        existing.is_active = True
        existing.is_valid = True
        existing.last_verified_at = now
        existing.remark = remark
        existing.save()
        print(f"[export_cookie] Updated CookieConfig id={existing.id} for platform={platform}")
        return

    cookie = CookieConfig.objects.create(
        platform=platform,
        name=name,
        cookies=cookie_str,
        is_active=True,
        is_valid=True,
        last_verified_at=now,
        remark=remark,
    )
    print(f"[export_cookie] Created CookieConfig id={cookie.id} for platform={platform}")


async def run_export(args: argparse.Namespace) -> int:
    configure_runtime(args.platform, use_cdp=not args.no_cdp)
    crawler_cls, login_cls = load_platform_components(args.platform)
    crawler = crawler_cls()
    browser_context = None

    async with async_playwright() as playwright:
        try:
            if config.ENABLE_CDP_MODE:
                browser_context = await crawler.launch_browser_with_cdp(
                    playwright,
                    None,
                    getattr(crawler, "user_agent", None),
                    headless=False,
                )
            else:
                browser_context = await crawler.launch_browser(
                    playwright.chromium,
                    None,
                    getattr(crawler, "user_agent", None),
                    headless=False,
                )
                await browser_context.add_init_script(path="libs/stealth.min.js")

            crawler.browser_context = browser_context
            page = await prepare_page(args.platform, crawler, browser_context)
            print(f"[export_cookie] Browser page opened for platform={args.platform}.")

            has_cookie = await has_login_cookie(args.platform, browser_context)
            session_valid = False
            if has_cookie:
                session_valid = await verify_existing_session(
                    args.platform,
                    crawler,
                    browser_context,
                )

            if session_valid:
                print("[export_cookie] Existing login session verified, exporting cookie directly.")
            else:
                if has_cookie:
                    print("[export_cookie] Existing cookies detected but session is invalid. Fresh QR login is required.")
                print("[export_cookie] Waiting for QR login. Please scan the browser page now.")
                login_obj = login_cls(
                    login_type="qrcode",
                    login_phone="",
                    browser_context=browser_context,
                    context_page=page,
                    cookie_str="",
                )
                await login_obj.begin()

            await post_login_prepare(args.platform, crawler, page, browser_context)
            cookie_str = await export_cookie_string(args.platform, browser_context)
            if not cookie_str:
                raise RuntimeError(f"Cookie export failed for platform={args.platform}")

            print("\n=== COOKIE_BEGIN ===")
            print(cookie_str)
            print("=== COOKIE_END ===\n")

            if args.save:
                await asyncio.to_thread(
                    save_cookie,
                    args.platform,
                    cookie_str,
                    args.name,
                    args.remark,
                )

            return 0
        finally:
            if getattr(crawler, "cdp_manager", None):
                try:
                    await crawler.cdp_manager.cleanup(force=True)
                except Exception:
                    pass
            elif browser_context is not None:
                try:
                    await browser_context.close()
                except Exception:
                    pass


def main() -> int:
    args = parse_args()
    return asyncio.run(run_export(args))


if __name__ == "__main__":
    raise SystemExit(main())

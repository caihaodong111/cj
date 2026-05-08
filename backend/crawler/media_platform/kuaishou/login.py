# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/kuaishou/login.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


import asyncio
import functools
import sys
from typing import Optional, Sequence

from playwright.async_api import BrowserContext, Page
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

import config
from base.base_crawler import AbstractLogin
from tools.qr_bridge import write_status
from tools import utils

LOGIN_TRIGGER_SELECTORS = (
    "xpath=//p[text()='登录']",
    "xpath=//button[contains(., '登录')]",
    "xpath=//div[@role='button' and contains(., '登录')]",
    "text=登录",
)

QRCODE_SELECTORS = (
    "xpath=//div[contains(@class, 'qrcode-img')]//img",
    "xpath=//img[contains(@alt, '二维码')]",
    "xpath=//div[contains(@class, 'login')]//img[contains(@src, 'data:image')]",
)


class KuaishouLogin(AbstractLogin):
    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext,
                 context_page: Page,
                 login_phone: Optional[str] = "",
                 cookie_str: str = ""
                 ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    async def begin(self):
        """Start login xiaohongshu"""
        utils.logger.info("[KuaishouLogin.begin] Begin login kuaishou ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[KuaishouLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...")

    async def _is_logged_in_once(self) -> bool:
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        return bool(cookie_dict.get("passToken"))

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self) -> bool:
        """
            Check if the current login status is successful and return True otherwise return False
            retry decorator will retry 20 times if the return value is False, and the retry interval is 1 second
            if max retry times reached, raise RetryError
        """
        return await self._is_logged_in_once()

    async def login_by_qrcode(self):
        """login kuaishou website and keep webdriver login state"""
        utils.logger.info("[KuaishouLogin.login_by_qrcode] Begin login kuaishou by qrcode ...")
        await self._wait_for_page_stable()
        if await self._is_logged_in_once():
            utils.logger.info("[KuaishouLogin.login_by_qrcode] Existing login session detected, skip QR login.")
            write_status("ks", "success")
            return

        qrcode_img_selector = await self._wait_for_any_selector(QRCODE_SELECTORS, timeout_ms=5000)
        if not qrcode_img_selector:
            clicked_selector = await self._click_first_available(LOGIN_TRIGGER_SELECTORS)
            if clicked_selector:
                utils.logger.info(f"[KuaishouLogin.login_by_qrcode] triggered login entry via selector: {clicked_selector}")
            await asyncio.sleep(1)
            qrcode_img_selector = await self._wait_for_any_selector(QRCODE_SELECTORS, timeout_ms=10000)

        base64_qrcode_img = None
        if qrcode_img_selector:
            base64_qrcode_img = await utils.find_login_qrcode(
                self.context_page,
                selector=qrcode_img_selector
            )
        if not base64_qrcode_img:
            utils.logger.info("[KuaishouLogin.login_by_qrcode] login failed , have not found qrcode please check ....")
            write_status("ks", "failed")
            sys.exit()


        # show login qrcode
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img, "ks")
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[KuaishouLogin.login_by_qrcode] waiting for scan code login, remaining time is 20s")
        try:
            await self.check_login_state()
        except RetryError:
            write_status("ks", "failed")
            utils.logger.info("[KuaishouLogin.login_by_qrcode] Login kuaishou failed by qrcode login method ...")
            sys.exit()

        write_status("ks", "success")
        wait_redirect_seconds = 5
        utils.logger.info(f"[KuaishouLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_mobile(self):
        pass

    async def login_by_cookies(self):
        utils.logger.info("[KuaishouLogin.login_by_cookies] Begin login kuaishou by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".kuaishou.com",
                'path': "/"
            }])
        try:
            await self.context_page.goto("https://www.kuaishou.com/?isHome=1", wait_until="domcontentloaded")
        except Exception as exc:
            utils.logger.warning(f"[KuaishouLogin.login_by_cookies] Failed to refresh homepage after setting cookies: {exc}")
        await self._wait_for_page_stable()

    async def _wait_for_page_stable(self, timeout_ms: int = 5000) -> None:
        try:
            await self.context_page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass
        try:
            await self.context_page.wait_for_load_state("networkidle", timeout=timeout_ms)
        except Exception:
            pass

    async def _wait_for_any_selector(self, selectors: Sequence[str], timeout_ms: int = 5000) -> Optional[str]:
        deadline = asyncio.get_running_loop().time() + timeout_ms / 1000
        while asyncio.get_running_loop().time() < deadline:
            for selector in selectors:
                try:
                    await self.context_page.locator(selector).first.wait_for(state="visible", timeout=500)
                    return selector
                except Exception:
                    continue
        return None

    async def _click_first_available(self, selectors: Sequence[str], timeout_ms: int = 3000) -> Optional[str]:
        deadline = asyncio.get_running_loop().time() + timeout_ms / 1000
        while asyncio.get_running_loop().time() < deadline:
            for selector in selectors:
                try:
                    locator = self.context_page.locator(selector).first
                    await locator.wait_for(state="visible", timeout=500)
                    await locator.click(timeout=1000)
                    return selector
                except Exception:
                    continue
        return None

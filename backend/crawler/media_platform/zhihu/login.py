# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/zhihu/login.py
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


# -*- coding: utf-8 -*-
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
    "button.SignFlow-tab",
    "xpath=//button[contains(., '登录')]",
    "text=登录",
)

QRCODE_SELECTORS = (
    "canvas.Qrcode-qrcode",
    "xpath=//canvas[contains(@class, 'Qrcode-qrcode')]",
)


class ZhiHuLogin(AbstractLogin):

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

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self) -> bool:
        """
        Check if the current login status is successful and return True otherwise return False
        Returns:

        """
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        current_web_session = cookie_dict.get("z_c0")
        if current_web_session:
            return True
        return False

    async def begin(self):
        """Start login zhihu"""
        utils.logger.info("[ZhiHu.begin] Begin login zhihu ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[ZhiHu.begin]I nvalid Login Type Currently only supported qrcode or phone or cookies ...")

    async def login_by_mobile(self):
        """Login zhihu by mobile"""
        # todo implement login by mobile

    async def login_by_qrcode(self):
        """login zhihu website and keep webdriver login state"""
        utils.logger.info("[ZhiHu.login_by_qrcode] Begin login zhihu by qrcode ...")
        await self._wait_for_page_stable()
        qrcode_img_selector = await self._wait_for_any_selector(QRCODE_SELECTORS, timeout_ms=10000)
        # find login qrcode
        base64_qrcode_img = None
        if not qrcode_img_selector:
            await self._click_first_available(LOGIN_TRIGGER_SELECTORS)
            await asyncio.sleep(1)
            qrcode_img_selector = await self._wait_for_any_selector(QRCODE_SELECTORS, timeout_ms=10000)
        if qrcode_img_selector:
            base64_qrcode_img = await utils.find_qrcode_img_from_canvas(
                self.context_page,
                canvas_selector=qrcode_img_selector
            )
        if not base64_qrcode_img:
            utils.logger.info("[ZhiHu.login_by_qrcode] login failed , have not found qrcode please check ....")
            if not base64_qrcode_img:
                write_status("zhihu", "failed")
                sys.exit()

        # show login qrcode
        # fix issue #12
        # we need to use partial function to call show_qrcode function and run in executor
        # then current asyncio event loop will not be blocked
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img, "zhihu")
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[ZhiHu.login_by_qrcode] waiting for scan code login, remaining time is 120s")
        try:
            await self.check_login_state()

        except RetryError:
            write_status("zhihu", "failed")
            utils.logger.info("[ZhiHu.login_by_qrcode] Login zhihu failed by qrcode login method ...")
            sys.exit()

        write_status("zhihu", "success")
        wait_redirect_seconds = 5
        utils.logger.info(
            f"[ZhiHu.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_cookies(self):
        """login zhihu website by cookies"""
        utils.logger.info("[ZhiHu.login_by_cookies] Begin login zhihu by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".zhihu.com",
                'path': "/"
            }])
        try:
            await self.context_page.goto("https://www.zhihu.com", wait_until="domcontentloaded")
        except Exception as exc:
            utils.logger.warning(f"[ZhiHu.login_by_cookies] Failed to refresh zhihu homepage after setting cookies: {exc}")
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

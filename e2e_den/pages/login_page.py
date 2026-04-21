"""
LoginPage - 로그인 페이지 엘리먼트 및 동작 정의
대상: https://member.denall.com/sso-login?channel-id=mcs&redirect-uri=https://osstem.com
SSO 로그인 후 osstem.com으로 리다이렉트됨
"""

import time
import logging

from pages.base_page import BasePage
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

SSO_DOMAIN      = "member.denall.com"
REDIRECT_DOMAIN = "osstem.com"


class LoginPage(BasePage):

    # ── 엘리먼트 ─────────────────────────────────────────────────────────────
    USERNAME  = ("css", "input[type='text'], input[name='username'], "
                        "input[name='userId'], input[name='id'], input[name='loginId']")
    PASSWORD  = ("css", "input[type='password']")
    LOGIN_BTN        = ("css", "button.btn-fill.dark.w-100")
    # 로그인 실패 시 노출되는 모달
    # <div class="modal-content"><div class="modal-body"><div class="text-center">...</div>
    ERROR_MSG        = ("css", ".modal-content .modal-body .text-center")
    ERROR_CONFIRM_BTN = ("css", ".modal-content .btn-fill.orange")

    # ── 내부 헬퍼 ─────────────────────────────────────────────────────────────
    def _type_humanlike(self, locator, text: str) -> None:
        """
        사이트가 자동화 입력을 감지할 경우를 대비해
        필드를 클릭 → clear → 한 글자씩 입력 (JS 이벤트 트리거 포함)
        """
        element = self.find(locator)
        self._safe_click(element)
        element.clear()
        # JS로 value를 직접 세팅한 뒤 input/change 이벤트를 강제로 발생시킴
        self.driver.execute_script(
            "arguments[0].value = '';"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            element
        )
        for char in text:
            element.send_keys(char)
            time.sleep(0.05)

    # ── 동작 ─────────────────────────────────────────────────────────────────
    def login(self, username: str, password: str) -> None:
        try:
            logger.info("로그인 시도: %s / (현재 URL: %s)", username, self.get_current_url())
            self._type_humanlike(self.USERNAME, username)
            self._type_humanlike(self.PASSWORD, password)
            self.sleep(0.3)
            self.click(self.LOGIN_BTN)
            logger.info("로그인 버튼 클릭 완료")
        except Exception as e:
            self.screenshot("login_fail")
            raise RuntimeError("로그인 동작 실패: {0}".format(e))

    def login_with_enter(self, username: str, password: str) -> None:
        """비밀번호 필드에서 엔터키로 폼 제출"""
        try:
            self._type_humanlike(self.USERNAME, username)
            self._type_humanlike(self.PASSWORD, password)
            self.sleep(0.3)
            self.find(self.PASSWORD).send_keys(Keys.ENTER)
        except Exception as e:
            self.screenshot("login_enter_fail")
            raise RuntimeError("엔터키 로그인 실패: {0}".format(e))

    def get_error_message(self) -> str:
        """에러 모달 텍스트를 반환하고 확인 버튼으로 모달을 닫음."""
        if not self.is_present(self.ERROR_MSG, timeout=4):
            return ""
        message = self.get_text(self.ERROR_MSG)
        self._close_error_modal()
        return message

    def _close_error_modal(self) -> None:
        """에러 모달의 확인 버튼 클릭으로 모달 닫기."""
        try:
            self.driver.execute_script(
                "arguments[0].click();",
                self.find(self.ERROR_CONFIRM_BTN)
            )
        except Exception:
            pass

    def is_login_failed(self) -> bool:
        """에러 모달이 노출되거나 SSO 도메인에 머무는 경우 실패로 판단."""
        self.sleep(3)
        url = self.get_current_url()
        logger.info("로그인 실패 판단 — 현재 URL: %s", url)
        has_modal = self.is_present(self.ERROR_MSG, timeout=3)
        if has_modal:
            self._close_error_modal()
        return has_modal or SSO_DOMAIN in url

    def is_login_success(self) -> bool:
        """osstem.com으로 리다이렉트된 경우 성공으로 판단"""
        try:
            self.wait_for_url_contains(REDIRECT_DOMAIN, timeout=20)
            url = self.get_current_url()
            logger.info("로그인 성공 판단 — 현재 URL: %s", url)
            return REDIRECT_DOMAIN in url
        except Exception:
            logger.warning("로그인 성공 대기 타임아웃 — 현재 URL: %s", self.get_current_url())
            return False

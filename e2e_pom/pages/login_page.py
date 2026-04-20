"""
LoginPage - 로그인 페이지 엘리먼트 및 동작 정의
"""

from pages.base_page import BasePage


class LoginPage(BasePage):

    # ── 엘리먼트 ─────────────────────────────────────────────────────────────
    USERNAME  = ("name", "USID")
    PASSWORD  = ("css", "input[type='password']")
    LOGIN_BTN = ("css", ".btn.btn-blue") #("css", "button[type='submit']")
    ERROR_MSG = ("css",".errorMsg")
    TOAST_MSG = ("class","toast-error")
    SUCCESS_MSG = ("class", "success-message")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    def login(self, username: str, password: str) -> None:
        try:
            self.type_text(self.USERNAME, username)
            self.type_text(self.PASSWORD, password)
            self.click(self.LOGIN_BTN)
        except Exception as e:
            self.screenshot("login_fail")
            raise RuntimeError("로그인 동작 실패: {0}".format(e))

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MSG) if self.is_present(self.ERROR_MSG, timeout=3) else ""

    def is_login_failed(self) -> bool:
        return self.is_present(self.TOAST_MSG, timeout=3)

    def is_login_success(self) -> bool:
        return self.is_present(self.SUCCESS_MSG, timeout=3)

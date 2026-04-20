"""
MainPage - 메인/공통 페이지 엘리먼트 및 동작 정의
GNB, 공통 팝업 등 사이트 전역에서 사용하는 요소
"""

from pages.base_page import BasePage


class MainPage(BasePage):

    # ── 엘리먼트 ─────────────────────────────────────────────────────────────
    # GNB_LOGIN_LINK  = ("partial_link_text", "로그인")
    # GNB_LOGOUT_LINK = ("partial_link_text", "로그아웃")
    # GNB_MYPAGE_LINK = ("partial_link_text", "마이페이지")
    POPUP_CLOSE_BTN = ("css", "button[aria-label='button']")
    TOAST_MSG       = ("class", "toast-message")
    USER_PROFILE    = ("css", "span.font-semibold")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    # def go_to_login(self) -> None:
    #     self.click(self.GNB_LOGIN_LINK)

    # def logout(self) -> None:
    #     self.click(self.GNB_LOGOUT_LINK)

    # def is_logged_in(self) -> bool:
    #     return self.is_present(self.GNB_LOGOUT_LINK, timeout=3)

    def close_popup_if_present(self) -> None:
        if self.is_present(self.POPUP_CLOSE_BTN, timeout=2):
            self.click(self.POPUP_CLOSE_BTN)

    # def get_toast_message(self) -> str:
    #     return self.get_text(self.TOAST_MSG) if self.is_present(self.TOAST_MSG, timeout=3) else ""

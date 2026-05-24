"""
MainPage - 메인/로그인 후 페이지 엘리먼트 및 동작 정의
대상: https://osstem.com/desktop
"""

import logging
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class MainPage(BasePage):

    # ── GNB / LNB ─────────────────────────────────────────────────────────────
    GNB_NAV = ("css", "nav.map-lnb")
    GNB_MENU_ITEMS = ("css", "nav.map-lnb button")
    GNB_LOGIN_LINK = ("css", "a[href*='login'], .btn-login, .login-link")
    GNB_MYPAGE_LINK = ("css", "a[href='/desktop/history']")

    USER_INFO = ("css", ".userInfo")
    USER_PROFILE = ("id", "userName")

    def _gnb_query_all(self, css: str, timeout: int = 5) -> list:
        """company-gnb Shadow DOM 안에서 CSS 셀렉터로 요소 목록 반환.
        company-gnb는 Vue SPA 렌더링으로 늦게 삽입되므로 출현 대기 포함.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return !!document.querySelector('company-gnb')")
            )
            return self.driver.execute_script(
                """
                var host = document.querySelector('company-gnb');
                if (!host || !host.shadowRoot) return [];
                return Array.from(host.shadowRoot.querySelectorAll(arguments[0]));
                """,
                css,
            ) or []
        except Exception as e:
            logger.debug(f"_gnb_query_all({css!r}) 실패: {e}")
            return []

    def _gnb_debug_info(self) -> dict:
        """진단용: company-gnb 존재 여부 및 shadow root 내 주요 클래스 목록 반환."""
        try:
            return self.driver.execute_script("""
                var host = document.querySelector('company-gnb');
                if (!host) return {found: false};
                var root = host.shadowRoot;
                if (!root) return {found: true, shadowRoot: false};
                var classes = Array.from(root.querySelectorAll('*'))
                    .map(el => el.className)
                    .filter(c => c && typeof c === 'string')
                    .slice(0, 30);
                return {found: true, shadowRoot: true, classes: classes};
            """)
        except Exception as e:
            return {"error": str(e)}

    # ── 메인 배너 ─────────────────────────────────────────────────────────────
    BANNER = ("css", ".banner, .slider, .swiper, [class*='banner'], [class*='slider']")
    BANNER_NEXT = ("css", ".swiper-button-next, .banner-next, .slider-next, [class*='next']")
    BANNER_PREV = ("css", ".swiper-button-prev, .banner-prev, .slider-prev, [class*='prev']")

    # ── 공통 팝업 ─────────────────────────────────────────────────────────────
    POPUP = ("css", ".popup, .modal, [role='dialog']")
    POPUP_CLOSE_BTN = ("css", ".popup .close, .modal .close, button[aria-label*='close'], button[aria-label*='닫기']")

    # ── 푸터 ─────────────────────────────────────────────────────────────────
    FOOTER = ("css", "footer")
    FOOTER_LINKS = ("css", "footer a")

    # ── 공지/이벤트 ───────────────────────────────────────────────────────────
    NOTICE_SECTION = ("css", "[class*='notice'], [class*='board'], [class*='news']")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    def close_popup_if_present(self) -> None:
        if self.is_present(self.POPUP_CLOSE_BTN, timeout=2):
            self.click(self.POPUP_CLOSE_BTN)

    def go_to_login(self) -> None:
        self.click(self.GNB_LOGIN_LINK)

    def logout(self) -> None:
        """이름 트리거 클릭으로 드롭다운 열고 로그아웃 클릭 (Shadow DOM)."""
        triggers = self._gnb_query_all(".gnb-name-trigger")
        if triggers:
            self.driver.execute_script("arguments[0].click();", triggers[0])
        logout_links = self._gnb_query_all("a.gnb-name-item[href*='sso-logout']")
        if logout_links:
            self.driver.execute_script("arguments[0].click();", logout_links[0])

    def is_logged_in(self, timeout: int = 15) -> bool:
        """Shadow DOM GNB에서 .gnb-name-text 존재 여부로 로그인 상태 판단.
        company-gnb가 인증 상태를 비동기로 렌더링하므로 대기 필요.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(self._gnb_query_all(".gnb-name-text")) > 0
            )
            return True
        except Exception:
            logger.warning("is_logged_in FAILED — gnb_debug: %s", self._gnb_debug_info())
            return False

    def is_logged_out(self) -> bool:
        return self.is_present(self.GNB_LOGIN_LINK, timeout=3)

    def get_username(self) -> str:
        """Shadow DOM .gnb-name-text 텍스트 반환."""
        els = self._gnb_query_all(".gnb-name-text")
        if els:
            return els[0].text.strip()
        return ""

    def get_gnb_menu_items(self) -> list:
        """nav.map-lnb 내 버튼 목록 반환."""
        return self.find_all(self.GNB_MENU_ITEMS)

    def get_gnb_menu_texts(self) -> list:
        return [el.text for el in self.get_gnb_menu_items()]

    def get_footer_link_texts(self) -> list:
        return self.get_texts(self.FOOTER_LINKS)

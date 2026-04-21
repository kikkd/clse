"""
MainPage - 메인/로그인 후 페이지 엘리먼트 및 동작 정의
대상: https://osstem.com/desktop
"""

from pages.base_page import BasePage


class MainPage(BasePage):

    # ── GNB ──────────────────────────────────────────────────────────────────
    GNB_NAV         = ("css", "nav, header nav, .gnb, .header-nav")
    GNB_MENU_ITEMS  = ("css", "nav a, .gnb a, header a")
    GNB_LOGIN_LINK  = ("css", "a[href*='login'], .btn-login, .login-link")
    GNB_MYPAGE_LINK = ("css", "a[href='/desktop/history']")

    # 로그인 후 HTML 기준 셀렉터
    USER_INFO       = ("css", ".userInfo")               # 로그인 상태 컨테이너
    USER_PROFILE    = ("id",  "userName")                # <a id="userName">최종인 ...</a>
    GNB_LOGOUT_LINK = ("xpath", "//ul[contains(@class,'alertLogoutInner')]//a[normalize-space(text())='로그아웃']")

    # ── 메인 배너 ─────────────────────────────────────────────────────────────
    BANNER          = ("css", ".banner, .slider, .swiper, [class*='banner'], [class*='slider']")
    BANNER_NEXT     = ("css", ".swiper-button-next, .banner-next, .slider-next, [class*='next']")
    BANNER_PREV     = ("css", ".swiper-button-prev, .banner-prev, .slider-prev, [class*='prev']")

    # ── 공통 팝업 ─────────────────────────────────────────────────────────────
    POPUP           = ("css", ".popup, .modal, [role='dialog']")
    POPUP_CLOSE_BTN = ("css", ".popup .close, .modal .close, button[aria-label*='close'], button[aria-label*='닫기']")

    # ── 푸터 ─────────────────────────────────────────────────────────────────
    FOOTER          = ("css", "footer")
    FOOTER_LINKS    = ("css", "footer a")

    # ── 공지/이벤트 ───────────────────────────────────────────────────────────
    NOTICE_SECTION  = ("css", "[class*='notice'], [class*='board'], [class*='news']")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    def close_popup_if_present(self) -> None:
        if self.is_present(self.POPUP_CLOSE_BTN, timeout=2):
            self.click(self.POPUP_CLOSE_BTN)

    def go_to_login(self) -> None:
        self.click(self.GNB_LOGIN_LINK)

    def logout(self) -> None:
        """userName 클릭으로 드롭다운 열고 로그아웃 클릭"""
        self.click(self.USER_PROFILE)
        self.click(self.GNB_LOGOUT_LINK)

    def is_logged_in(self) -> bool:
        """.userInfo 컨테이너 또는 #userName 존재 여부로 로그인 상태 판단"""
        return (
            self.is_present(self.USER_INFO, timeout=5)
            or self.is_present(self.USER_PROFILE, timeout=5)
        )

    def is_logged_out(self) -> bool:
        return self.is_present(self.GNB_LOGIN_LINK, timeout=3)

    def get_username(self) -> str:
        """로그인된 사용자 이름 텍스트 반환 (아이콘 텍스트 제외)"""
        element = self.find(self.USER_PROFILE)
        # innerText에서 <i> 태그 텍스트를 제거하기 위해 JS 사용
        return self.driver.execute_script(
            "return arguments[0].childNodes[0].textContent.trim();", element
        )

    def get_gnb_menu_texts(self) -> list:
        return self.get_texts(self.GNB_MENU_ITEMS)

    def get_footer_link_texts(self) -> list:
        return self.get_texts(self.FOOTER_LINKS)

"""
test_main.py - 메인 페이지 공통 시나리오 테스트
대상: https://osstem.com/desktop (로그인 후 랜딩 페이지)
"""

import pytest
from pages.main_page import MainPage
from pages.login_page import LoginPage

MAIN_URL  = "https://osstem.com/desktop"
LOGIN_URL = "https://osstem.com/desktop/login"


@pytest.fixture
def main_page(logged_in_browser):
    page = MainPage(logged_in_browser)
    # page.navigate(MAIN_URL)
    # page.close_popup_if_present()
    return page


@pytest.fixture
def main_page_no_login(browser):
    """비로그인 상태의 메인 페이지"""
    page = MainPage(browser)
    page.navigate(MAIN_URL)
    return page


class TestMain:

    def test_페이지_로딩(self, main_page):
        """메인 페이지 정상 로딩 확인."""
        title = main_page.get_title()
        assert title != "", "타이틀이 비어있으면 안 됨"

    def test_URL_확인(self, main_page):
        """메인 페이지 URL에 'osstem.com'이 포함되어야 함."""
        assert "osstem.com" in main_page.get_current_url(), \
            "URL에 'osstem.com'이 포함되어야 함"

    def test_로그인_사용자_확인(self, main_page):
        """로그인 후 .userInfo 컨테이너와 #userName이 GNB에 표시되어야 함."""
        assert main_page.is_logged_in(), \
            "로그인 후 .userInfo / #userName이 표시되어야 함"
        username = main_page.get_username()
        assert username != "", "사용자 이름이 비어있으면 안 됨"

    def test_GNB_메뉴_노출(self, main_page):
        """GNB 네비게이션 메뉴가 1개 이상 존재해야 함."""
        items = main_page.find_all(main_page.GNB_MENU_ITEMS)
        assert len(items) > 0, "GNB 메뉴 항목이 1개 이상이어야 함"

    def test_푸터_노출(self, main_page):
        """푸터가 페이지에 존재해야 함."""
        assert main_page.is_present(main_page.FOOTER), \
            "푸터 영역이 존재해야 함"

    def test_배너_노출(self, main_page):
        """메인 배너/슬라이더가 존재해야 함."""
        assert main_page.is_present(main_page.BANNER, timeout=5), \
            "메인 배너가 존재해야 함"

    def test_비로그인_접근시_리다이렉트(self, main_page_no_login):
        """비로그인 상태에서 로그인 버튼 또는 로그인 페이지로 리다이렉트 확인."""
        url = main_page_no_login.get_current_url()
        has_login_btn = main_page_no_login.is_present(main_page_no_login.GNB_LOGIN_LINK, timeout=5)
        # 로그인 페이지로 리다이렉트 되거나, 로그인 버튼이 노출되어야 함
        assert "login" in url or has_login_btn, \
            "비로그인 상태에서는 로그인 페이지로 이동하거나 로그인 버튼이 보여야 함"

    def test_로그아웃(self, main_page):
        """로그아웃 후 로그인 페이지로 이동 또는 로그인 버튼 노출 확인."""
        if not main_page.is_present(main_page.GNB_LOGOUT_LINK, timeout=3):
            pytest.skip("로그아웃 버튼을 찾을 수 없음 — 선택자 확인 필요")
        main_page.logout()
        main_page.sleep(1)
        url = main_page.get_current_url()
        has_login = main_page.is_present(main_page.GNB_LOGIN_LINK, timeout=5)
        assert "login" in url or has_login, \
            "로그아웃 후 로그인 페이지 이동 또는 로그인 버튼이 노출되어야 함"

    def test_보호페이지_직접_URL_접근(self, browser):
        """비로그인 상태에서 보호 페이지 직접 접근 시 리다이렉트 확인."""
        page = MainPage(browser)
        page.navigate(MAIN_URL)
        page.sleep(2)
        url = page.get_current_url()
        has_login_btn = page.is_present(page.GNB_LOGIN_LINK, timeout=5)
        assert "login" in url or has_login_btn, \
            "비인증 접근 시 로그인 유도가 있어야 함"

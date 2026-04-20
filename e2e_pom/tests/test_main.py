"""
test_main.py - 메인 페이지 공통 시나리오 테스트
"""

import pytest
from pages.main_page import MainPage

# MAIN_URL = "https://example.com"


@pytest.fixture
def main_page(logged_in_browser):
    page = MainPage(logged_in_browser)
    # page.navigate(MAIN_URL)
    page.close_popup_if_present()
    return page


class TestMain:

    def test_페이지_로딩(self, main_page):
        """메인 페이지 정상 로딩 확인."""
        assert main_page.get_title() != "", "타이틀이 비어있으면 안 됨"
        assert "medical" in main_page.get_current_url()

    def test_로그인_사용자_확인(self, main_page):
        """로그인 후 GNB에 사용자 이름 표시 확인."""
        assert main_page.is_present(main_page.USER_PROFILE), \
            "로그인 후 사용자 이름이 표시되어야 함"
        username = main_page.get_text(main_page.USER_PROFILE)
        assert username != "", "사용자 이름이 비어있으면 안 됨"

    # def test_로그인_페이지_이동(self, main_page):
    #     """로그인 링크 클릭 후 로그인 페이지 이동 확인."""
    #     main_page.go_to_login()
    #     assert "login" in main_page.get_current_url(), \
    #         "로그인 페이지 URL에 'login'이 포함되어야 함"

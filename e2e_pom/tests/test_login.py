"""
test_login.py - 로그인 시나리오 테스트
"""

import pytest
from pages.login_page import LoginPage

LOGIN_URL = "https://hippo2qa.osstem.com/web/login"


@pytest.fixture
def login_page(browser):
    page = LoginPage(browser)
    page.navigate(LOGIN_URL)
    return page


class TestLogin:
    def test_정상_로그인(self, login_page):
        """유효한 계정으로 로그인 성공 확인."""
        login_page.login("testdoc02@dev00003", "mpms1234!@")
        login_page.wait_for_url_contains("medical")  # URL 바뀔 때까지 대기
        # print(login_page.get_current_url())
        assert "medical" in login_page.get_current_url(), \
            "로그인 후 dashboard medical로 이동해야 함"

    def test_잘못된_비밀번호(self, login_page):
        """잘못된 비밀번호 입력 시 에러 메시지 노출 확인."""
        login_page.login("testdoc01@dev00003", "wrongpw")
        assert login_page.is_login_failed(), \
            "잘못된 비밀번호 시 에러 메시지가 표시되어야 함"

    def test_아이디_미입력(self, login_page):
        """아이디 미입력 시 에러 메시지 노출 확인."""
        login_page.login("", "mpms1234!@")
        assert login_page.is_login_failed(), \
            "아이디 미입력 시 에러 메시지가 표시되어야 함"

    def test_비밀번호_미입력(self, login_page):
        """비밀번호 미입력 시 에러 메시지 노출 확인."""
        login_page.login("qqqq", "")
        assert login_page.is_login_failed(), \
            "비밀번호 미입력 시 에러 메시지가 표시되어야 함"

    def test_에러_메시지_내용(self, login_page):
        """에러 메시지 텍스트 확인."""
        login_page.login("qqqq@dev00003", "wrongpw")
        error = login_page.get_error_message()
        assert error != "", "에러 메시지가 비어있으면 안 됨"

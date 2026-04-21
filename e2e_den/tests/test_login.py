"""
test_login.py - 로그인 시나리오 테스트

로그인 절차:
  1. osstem.com/desktop/map 접속
  2. GNB '로그인' 버튼 클릭 → member.denall.com SSO 페이지 이동
  3. SSO 페이지에서 ID/PW 입력 후 로그인
  4. 성공 시 osstem.com으로 리다이렉트
"""

import pytest
from pages.map_page import MapPage
from pages.login_page import LoginPage

MAP_URL    = "https://osstem.com/desktop/map"
SSO_DOMAIN = "member.denall.com"
VALID_ID   = "whddls66"
VALID_PW   = "q2w3e4r5!d"


@pytest.fixture
def login_page(browser):
    """map 페이지에서 로그인 버튼 클릭 후 SSO 로그인 페이지 반환."""
    map_page = MapPage(browser)
    map_page.navigate(MAP_URL)
    map_page.click_login_btn()
    map_page.wait_for_url_contains(SSO_DOMAIN, timeout=10)
    return LoginPage(browser)


class TestLogin:
    def test_정상_로그인(self, login_page):
        """유효한 계정으로 로그인 성공 후 osstem.com으로 리다이렉트 확인."""
        login_page.login(VALID_ID, VALID_PW)
        assert login_page.is_login_success(), \
            "로그인 성공 후 osstem.com으로 리다이렉트 되어야 함"

    def test_잘못된_비밀번호(self, login_page):
        """잘못된 비밀번호 입력 시 SSO 페이지에 머물거나 에러 메시지 노출 확인."""
        login_page.login(VALID_ID, "wrongpassword!")
        assert login_page.is_login_failed(), \
            "잘못된 비밀번호 시 로그인이 실패해야 함"

    def test_아이디_미입력(self, login_page):
        """아이디 미입력 시 에러 처리 확인."""
        login_page.login("", VALID_PW)
        assert login_page.is_login_failed(), \
            "아이디 미입력 시 로그인이 실패해야 함"

    def test_비밀번호_미입력(self, login_page):
        """비밀번호 미입력 시 에러 처리 확인."""
        login_page.login(VALID_ID, "")
        assert login_page.is_login_failed(), \
            "비밀번호 미입력 시 로그인이 실패해야 함"

    def test_아이디_비밀번호_모두_미입력(self, login_page):
        """ID/PW 모두 미입력 시 에러 처리 확인."""
        login_page.login("", "")
        assert login_page.is_login_failed(), \
            "ID/PW 모두 미입력 시 로그인이 실패해야 함"

    def test_존재하지_않는_아이디(self, login_page):
        """존재하지 않는 계정으로 로그인 시 실패 확인."""
        login_page.login("notexistuser999", "wrongpassword!")
        assert login_page.is_login_failed(), \
            "없는 계정 로그인 시 SSO 페이지에 머물러야 함"

    def test_에러_메시지_노출(self, login_page):
        """잘못된 자격증명 시 에러 메시지 텍스트가 비어있지 않은지 확인."""
        login_page.login("wronguser", "wrongpass!")
        error = login_page.get_error_message()
        assert error != "", "에러 메시지가 비어있으면 안 됨"

    def test_엔터키_로그인(self, login_page):
        """비밀번호 필드에서 엔터키로 로그인 제출 후 osstem.com 리다이렉트 확인."""
        login_page.login_with_enter(VALID_ID, VALID_PW)
        assert login_page.is_login_success(), \
            "엔터키 로그인 후 osstem.com으로 리다이렉트 되어야 함"

    def test_SSO_페이지_타이틀(self, login_page):
        """SSO 로그인 페이지 타이틀이 비어있지 않은지 확인."""
        assert login_page.get_title() != "", "페이지 타이틀이 비어있으면 안 됨"

    def test_SSO_페이지_도메인(self, login_page):
        """로그인 버튼 클릭 후 SSO 도메인(member.denall.com)으로 이동했는지 확인."""
        assert SSO_DOMAIN in login_page.get_current_url(), \
            "로그인 버튼 클릭 후 member.denall.com으로 이동해야 함"

    def test_map_로그인_버튼_존재(self, browser):
        """비로그인 상태에서 map 페이지에 로그인 버튼이 노출되어야 함."""
        map_page = MapPage(browser)
        map_page.navigate(MAP_URL)
        assert map_page.is_present(MapPage.LOGIN_BTN, timeout=10), \
            "비로그인 상태에서 map 페이지에 로그인 버튼이 있어야 함"

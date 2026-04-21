"""
conftest.py - pytest 전역 fixture 및 공통 설정
브라우저 생성/종료, 로그인 상태 유지, 전역 예외처리 담당

로그인 절차:
  1. osstem.com/desktop/map 접속
  2. GNB '로그인' 버튼 클릭
  3. member.denall.com SSO 페이지로 이동 대기
  4. ID/PW 입력 후 로그인
  5. osstem.com으로 리다이렉트 대기
"""

import pytest
from drivers.browser_factory import create_driver
from config.settings import BASE_URL
from pages.map_page import MapPage
from pages.login_page import LoginPage

MAP_URL   = "https://osstem.com/desktop/map"
MAIN_URL  = "https://osstem.com/desktop"
LOGIN_ID  = "whddls66"
LOGIN_PW  = "q2w3e4r5!d"
SSO_DOMAIN = "member.denall.com"


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome",
                     help="실행 브라우저: chrome | firefox | edge")
    parser.addoption("--url", action="store", default=BASE_URL,
                     help="테스트 대상 URL")


@pytest.fixture(scope="session")
def browser_name(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--url")


@pytest.fixture(scope="function")
def browser(browser_name):
    """테스트 함수마다 브라우저 새로 생성 후 종료."""
    driver = create_driver(browser_name)
    yield driver
    driver.quit()


def _do_login(browser):
    """
    공통 로그인 절차:
      map 페이지 → 로그인 버튼 클릭 → SSO 페이지 → 로그인 → osstem.com 리다이렉트
    """
    map_page = MapPage(browser)
    map_page.navigate(MAP_URL)
    map_page.click_login_btn()
    map_page.wait_for_url_contains(SSO_DOMAIN, timeout=10)

    login_page = LoginPage(browser)
    login_page.login(LOGIN_ID, LOGIN_PW)
    login_page.wait_for_url_contains("osstem.com", timeout=20)

    # 로그인 후 노출되는 팝업 자동 닫기
    post_page = MapPage(browser)
    post_page.close_popup_if_present()


@pytest.fixture(scope="function")
def logged_in_browser(browser):
    """로그인된 상태의 브라우저 반환. 로그인이 필요한 모든 테스트에서 사용."""
    _do_login(browser)
    yield browser


@pytest.fixture(autouse=True)
def dismiss_leftover_alert(browser):
    """테스트 종료 후 남아있는 alert 자동 닫기."""
    yield
    try:
        browser.switch_to.alert.dismiss()
    except Exception:
        pass

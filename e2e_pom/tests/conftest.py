"""
conftest.py - pytest 전역 fixture 및 공통 설정
브라우저 생성/종료, 로그인 상태 유지, 전역 예외처리 담당
"""

import pytest
from drivers.browser_factory import create_driver
from config.settings import BASE_URL
from pages.login_page import LoginPage

LOGIN_URL = "https://hippo2qa.osstem.com/web/login"
LOGIN_ID  = "testdoc01@dev00003"
LOGIN_PW  = "mpms1234!@"


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


@pytest.fixture(scope="function")
def logged_in_browser(browser):
    """로그인된 상태의 브라우저 반환. 로그인이 필요한 모든 테스트에서 사용."""
    page = LoginPage(browser)
    page.navigate(LOGIN_URL)
    page.login(LOGIN_ID, LOGIN_PW)
    page.wait_for_url_contains("medical")
    yield browser


@pytest.fixture(autouse=True)
def dismiss_leftover_alert(browser):
    """테스트 종료 후 남아있는 alert 자동 닫기."""
    yield
    try:
        browser.switch_to.alert.dismiss()
    except Exception:
        pass

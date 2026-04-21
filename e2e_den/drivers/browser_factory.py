"""
Browser Factory - 크로스 브라우저 드라이버 생성 모듈
지원: Chrome, Firefox, Edge, Safari
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.settings import BROWSER_OPTIONS, TIMEOUTS, SUPPORTED_BROWSERS


def _build_chrome(opts: dict) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if opts.get("headless"):
        options.add_argument("--headless=new")
    if opts.get("no_sandbox"):
        options.add_argument("--no-sandbox")
    if opts.get("disable_gpu"):
        options.add_argument("--disable-gpu")
    w, h = opts.get("window_size", (1920, 1080))
    options.add_argument(f"--window-size={w},{h}")
    options.add_argument("--disable-dev-shm-usage")

    # 자동화 감지 차단 — navigator.webdriver 플래그 및 자동화 배너 제거
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 비밀번호 저장 팝업 및 자동완성 비활성화
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
    })

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )
    # CDP로 navigator.webdriver 속성 숨기기
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


def _build_firefox(opts: dict) -> webdriver.Firefox:
    options = webdriver.FirefoxOptions()
    if opts.get("headless"):
        options.add_argument("--headless")
    return webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options,
    )


def _build_edge(opts: dict) -> webdriver.Edge:
    options = webdriver.EdgeOptions()
    if opts.get("headless"):
        options.add_argument("--headless=new")
    return webdriver.Edge(
        service=EdgeService(EdgeChromiumDriverManager().install()),
        options=options,
    )


def _build_safari(_opts: dict) -> webdriver.Safari:
    # Safari는 macOS 전용 — safaridriver가 활성화되어 있어야 함
    return webdriver.Safari()


_BUILDERS = {
    "chrome":  _build_chrome,
    "firefox": _build_firefox,
    "edge":    _build_edge,
    "safari":  _build_safari,
}


def create_driver(browser: str = "chrome") -> webdriver.Remote:
    """
    지정한 브라우저의 WebDriver 인스턴스를 생성하여 반환.

    Args:
        browser: 브라우저 이름 (chrome | firefox | edge | safari)

    Returns:
        WebDriver 인스턴스
    """
    browser = browser.lower().strip()
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError(
            f"지원하지 않는 브라우저: '{browser}'. "
            f"지원 목록: {SUPPORTED_BROWSERS}"
        )

    opts = BROWSER_OPTIONS.get(browser, {})
    driver = _BUILDERS[browser](opts)

    # implicit_wait은 explicit wait(WebDriverWait)과 함께 쓰면 충돌 → 0으로 고정
    driver.implicitly_wait(0)
    driver.set_page_load_timeout(TIMEOUTS["page_load"])
    driver.set_script_timeout(TIMEOUTS["script"])

    w, h = opts.get("window_size", (1920, 1080))
    driver.set_window_size(w, h)

    return driver

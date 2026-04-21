"""
Base Page - 모든 Page Object가 상속받는 기본 클래스
element_map 모듈에서 엘리먼트 로케이터를 가져와 동작을 수행한다.
"""

import os
import time
import logging

from typing import List, Optional, Tuple, Union

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from config.settings import TIMEOUTS, PATHS
from elements.element_map import get_element, get_all_maps, LOCATOR_TYPES

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUTS["explicit"])
        self._all_elements = get_all_maps()

    # ── 네비게이션 ────────────────────────────────────────────────────────────

    def navigate(self, url: str) -> None:
        logger.info(f"Navigate → {url}")
        self.driver.get(url)
        self._wait_for_page_ready()

    def _wait_for_page_ready(self) -> None:
        """document.readyState 가 complete 될 때까지 대기"""
        try:
            WebDriverWait(self.driver, TIMEOUTS["page_load"]).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass  # 타임아웃 시에도 계속 진행

    def go_back(self) -> None:
        self.driver.back()

    def go_forward(self) -> None:
        self.driver.forward()

    def refresh(self) -> None:
        self.driver.refresh()

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    # ── 엘리먼트 탐색 ─────────────────────────────────────────────────────────

    def _resolve(self, key_or_locator) -> Tuple:
        """
        key_or_locator:
          - str          → element_map 딕셔너리에서 (By.*, value) 반환
          - ("css", ...) → locator_type 문자열을 By.* 로 변환 후 반환
          - (By.*, ...)  → 이미 변환된 tuple, 그대로 사용
        """
        if isinstance(key_or_locator, str):
            return get_element(self._all_elements, key_or_locator)

        locator_type, locator_value = key_or_locator
        # 문자열 타입("css", "id" 등)이면 By.* 상수로 변환
        if isinstance(locator_type, str):
            key = locator_type.lower().strip()
            by = LOCATOR_TYPES.get(key)
            if by is None:
                raise ValueError(
                    "알 수 없는 locator_type: '{0}'. 사용 가능: {1}".format(
                        locator_type, list(LOCATOR_TYPES.keys())
                    )
                )
            # class 타입에 공백이 있으면(복합 클래스) CSS 선택자로 자동 변환
            # By.CLASS_NAME은 공백 포함 클래스명을 지원하지 않음
            if key == "class" and " " in locator_value.strip():
                from selenium.webdriver.common.by import By
                css_value = "." + ".".join(locator_value.strip().split())
                return (By.CSS_SELECTOR, css_value)
            return (by, locator_value)

        return key_or_locator

    def find(self, key_or_locator, timeout: int = None) -> WebElement:
        locator = self._resolve(key_or_locator)
        t = timeout or TIMEOUTS["explicit"]
        return WebDriverWait(self.driver, t).until(
            EC.presence_of_element_located(locator),
            message=f"Element not found: {locator}",
        )

    def find_all(self, key_or_locator, timeout: int = None) -> List[WebElement]:
        locator = self._resolve(key_or_locator)
        t = timeout or TIMEOUTS["explicit"]
        # presence_of_all_elements_located: 1개 이상 존재하면 즉시 반환, 없으면 timeout 후 빈 리스트
        try:
            return WebDriverWait(self.driver, t).until(
                EC.presence_of_all_elements_located(locator)
            )
        except Exception:
            return []

    def is_visible(self, key_or_locator, timeout: int = 5) -> bool:
        try:
            locator = self._resolve(key_or_locator)
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def is_present(self, key_or_locator, timeout: int = 5) -> bool:
        try:
            locator = self._resolve(key_or_locator)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def find_nth(self, key_or_locator, nth=1, timeout=None):
        # type: (any, int, Optional[int]) -> WebElement
        """
        동일 locator 중 nth번째 엘리먼트 반환 (1-based).
        예) class명이 같은 버튼 3개 중 2번째 → nth=2
        """
        elements = self.find_all(key_or_locator, timeout)
        count = len(elements)
        if count == 0:
            raise Exception("Elements not found: {0}".format(key_or_locator))
        if nth > count:
            raise Exception(
                "nth={0} 요청했지만 실제 엘리먼트는 {1}개: {2}".format(nth, count, key_or_locator)
            )
        logger.info("find_nth({0}) → {1}".format(nth, key_or_locator))
        return elements[nth - 1]

    # ── 클릭 ─────────────────────────────────────────────────────────────────

    def _safe_click(self, element) -> None:
        """
        엘리먼트 클릭 3단계 전략:
        1. hover(마우스 이동) → 일반 click  : 반응형 UI·드롭다운 대응
        2. scrollIntoView   → 일반 click  : 스크롤 위치 문제 대응
        3. scrollIntoView   → JS click    : overlay·animation 대응
        """
        actions = ActionChains(self.driver)
        # 1단계: 마우스를 엘리먼트 위로 이동 후 클릭
        try:
            actions.move_to_element(element).pause(0.3).click().perform()
            return
        except Exception:
            pass
        # 2단계: 스크롤 후 일반 클릭
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            time.sleep(0.3)
            element.click()
            return
        except Exception:
            pass
        # 3단계: 스크롤 후 JS 클릭
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        self.driver.execute_script("arguments[0].click();", element)
        logger.info("JS fallback click used")

    def click(self, key_or_locator) -> None:
        locator = self._resolve(key_or_locator)
        logger.info("Click → {0}".format(locator))
        try:
            element = WebDriverWait(self.driver, TIMEOUTS["explicit"]).until(
                EC.presence_of_element_located(locator)
            )
            self._safe_click(element)
        except Exception as e:
            raise Exception("클릭 실패 | locator={0} | 사유={1}".format(locator, e))

    def click_nth(self, key_or_locator, nth=1) -> None:
        """동일 locator 중 nth번째 엘리먼트 클릭 (1-based)."""
        element = self.find_nth(key_or_locator, nth)
        self._safe_click(element)
        logger.info("Click nth={0} → {1}".format(nth, key_or_locator))

    def js_click(self, key_or_locator) -> None:
        """일반 click이 안 될 때 JS로 클릭"""
        element = self.find(key_or_locator)
        self.driver.execute_script("arguments[0].click();", element)
        logger.info(f"JS Click → {key_or_locator}")

    def double_click(self, key_or_locator) -> None:
        element = self.find(key_or_locator)
        ActionChains(self.driver).double_click(element).perform()

    def right_click(self, key_or_locator) -> None:
        element = self.find(key_or_locator)
        ActionChains(self.driver).context_click(element).perform()

    # ── 입력 ─────────────────────────────────────────────────────────────────

    def type_text(self, key_or_locator, text, clear_first=True, nth=None):
        # type: (any, str, bool, Optional[int]) -> None
        element = self.find_nth(key_or_locator, nth) if nth else self.find(key_or_locator)
        if clear_first:
            element.clear()
        logger.info(f"Type '{text}' nth={nth} → {key_or_locator}")
        element.send_keys(text)

    def press_key(self, key_or_locator, key: str) -> None:
        """Keys 상수 문자열로 특수키 입력 (e.g. 'ENTER', 'TAB')"""
        element = self.find(key_or_locator)
        element.send_keys(getattr(Keys, key.upper()))

    def clear_field(self, key_or_locator) -> None:
        self.find(key_or_locator).clear()

    # ── 드롭다운 ─────────────────────────────────────────────────────────────

    def select_by_text(self, key_or_locator, text: str) -> None:
        Select(self.find(key_or_locator)).select_by_visible_text(text)

    def select_by_value(self, key_or_locator, value: str) -> None:
        Select(self.find(key_or_locator)).select_by_value(value)

    def select_by_index(self, key_or_locator, index: int) -> None:
        Select(self.find(key_or_locator)).select_by_index(index)

    # ── 마우스 이동 ───────────────────────────────────────────────────────────

    def hover(self, key_or_locator) -> None:
        element = self.find(key_or_locator)
        ActionChains(self.driver).move_to_element(element).perform()

    def scroll_to(self, key_or_locator) -> None:
        element = self.find(key_or_locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_to_top(self) -> None:
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # ── 텍스트/속성 추출 ──────────────────────────────────────────────────────

    def get_text(self, key_or_locator) -> str:
        return self.find(key_or_locator).text

    def get_attribute(self, key_or_locator, attr: str) -> str:
        return self.find(key_or_locator).get_attribute(attr)

    def get_texts(self, key_or_locator) -> List[str]:
        return [el.text for el in self.find_all(key_or_locator)]

    # ── 대기 ─────────────────────────────────────────────────────────────────

    def wait_for_visible(self, key_or_locator, timeout: int = None) -> WebElement:
        locator = self._resolve(key_or_locator)
        t = timeout or TIMEOUTS["explicit"]
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_invisible(self, key_or_locator, timeout: int = None) -> bool:
        locator = self._resolve(key_or_locator)
        t = timeout or TIMEOUTS["explicit"]
        return WebDriverWait(self.driver, t).until(
            EC.invisibility_of_element_located(locator)
        )

    def wait_for_url_contains(self, partial_url: str, timeout: int = None) -> bool:
        t = timeout or TIMEOUTS["explicit"]
        return WebDriverWait(self.driver, t).until(
            EC.url_contains(partial_url)
        )

    def wait_for_url_not_contains(self, partial_url: str, timeout: int = None) -> bool:
        t = timeout or TIMEOUTS["explicit"]
        return WebDriverWait(self.driver, t).until(
            lambda d: partial_url not in d.current_url
        )

    def wait_for_title_contains(self, partial_title: str, timeout: int = None) -> bool:
        t = timeout or TIMEOUTS["explicit"]
        return WebDriverWait(self.driver, t).until(
            EC.title_contains(partial_title)
        )

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    # ── Alert 처리 ────────────────────────────────────────────────────────────

    def accept_alert(self) -> str:
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text

    def dismiss_alert(self) -> str:
        alert = self.wait.until(EC.alert_is_present())
        text = alert.text
        alert.dismiss()
        return text

    # ── 스크린샷 ─────────────────────────────────────────────────────────────

    def screenshot(self, name: str = None, delay: float = 1.0) -> str:
        time.sleep(delay)
        os.makedirs(PATHS["screenshots"], exist_ok=True)
        filename = name or "screenshot_{0}".format(int(time.time()))
        path = os.path.join(PATHS["screenshots"], "{0}.png".format(filename))
        self.driver.save_screenshot(path)
        logger.info("Screenshot saved → {0}".format(path))
        return path

    # ── iframe ────────────────────────────────────────────────────────────────

    def switch_to_frame(self, key_or_locator) -> None:
        element = self.find(key_or_locator)
        self.driver.switch_to.frame(element)

    def switch_to_default(self) -> None:
        self.driver.switch_to.default_content()

    # ── 새 탭/창 ─────────────────────────────────────────────────────────────

    def switch_to_window(self, index: int = -1) -> None:
        self.driver.switch_to.window(self.driver.window_handles[index])

    def close_current_tab(self) -> None:
        self.driver.close()
        self.switch_to_window()

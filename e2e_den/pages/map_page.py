"""
MapPage - 지도 페이지 엘리먼트 및 동작 정의
대상: https://osstem.com/desktop/map
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class MapPage(BasePage):

    # ── 로그인 버튼 (비로그인 상태 GNB) ──────────────────────────────────────
    LOGIN_BTN           = ("xpath", "//button[@type='button' and normalize-space(text())='로그인']")

    # ── 지도 컨테이너 ─────────────────────────────────────────────────────────
    MAP_CONTAINER       = ("css", "#map, .map-container, [class*='map'], [id*='map']")

    # ── 검색 입력 ─────────────────────────────────────────────────────────────
    SEARCH_INPUT        = ("css", "input[placeholder*='검색'], input[placeholder*='병원'], "
                                  "input[placeholder*='치과'], input[type='text']")

    # ── 자동완성 드롭다운 (타이핑 후 JS 렌더링) ───────────────────────────────
    # <ul id="ac-listbox" role="listbox">
    AUTOCOMPLETE_BOX    = ("id",  "ac-listbox")
    # <li role="option" class="... search-bottom-row">
    AUTOCOMPLETE_ITEM   = ("css", "#ac-listbox li[role='option']")
    # 병원명: <span class="text-14 text-bold">
    AUTOCOMPLETE_NAME   = ("css", "#ac-listbox li[role='option'] span.text-14.text-bold")
    # 주소: <span class="addr-text">
    AUTOCOMPLETE_ADDR   = ("css", "#ac-listbox li[role='option'] span.addr-text")

    # ── 지역 필터 ─────────────────────────────────────────────────────────────
    REGION_SIDO         = ("css", "select:first-of-type, select[name*='sido'], .sido-select")
    REGION_GUGUN        = ("css", "select:nth-of-type(2), select[name*='gugun'], .gugun-select")

    # ── 결과 없음 ─────────────────────────────────────────────────────────────
    NO_RESULT_MSG       = ("css", ".no-result, .empty, .no-data, [class*='no-result']")

    # ── 공통 팝업 닫기 버튼 ──────────────────────────────────────────────────
    POPUP_CLOSE_BTN     = ("xpath", "//button[contains(@class,'btn-dark') and contains(.,'닫기')]")

    # ── 상세 팝업 ─────────────────────────────────────────────────────────────
    DETAIL_POPUP        = ("css", ".detail-popup, .info-window, [class*='popup']")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    def click_login_btn(self) -> None:
        self.click(self.LOGIN_BTN)

    def type_search(self, keyword: str) -> None:
        """검색어 입력 → 자동완성 드롭다운 대기"""
        self.type_text(self.SEARCH_INPUT, keyword)
        # 자동완성 드롭다운이 나타날 때까지 대기 (JS 렌더링)
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "ac-listbox"))
        )

    def search_with_enter(self, keyword: str) -> None:
        """검색어 입력 후 엔터 — 자동완성 없이 바로 검색 제출"""
        self.type_text(self.SEARCH_INPUT, keyword)
        self.press_key(self.SEARCH_INPUT, "ENTER")

    def has_autocomplete_results(self) -> bool:
        """자동완성 드롭다운에 항목이 1개 이상 있는지 확인"""
        items = self.find_all(self.AUTOCOMPLETE_ITEM)
        return len(items) > 0

    def get_autocomplete_count(self) -> int:
        return len(self.find_all(self.AUTOCOMPLETE_ITEM))

    def get_autocomplete_names(self) -> list:
        """자동완성 목록의 병원명 텍스트 리스트 반환"""
        return self.driver.execute_script(
            "return Array.from(document.querySelectorAll('#ac-listbox li[role=\"option\"] span.text-14.text-bold'))"
            ".map(el => el.innerText.trim());"
        )

    def click_first_autocomplete(self) -> None:
        """자동완성 드롭다운 첫 번째 항목 JS 클릭"""
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#ac-listbox li[role='option']"))
        )
        first = self.driver.find_element(By.CSS_SELECTOR, "#ac-listbox li[role='option']")
        self.driver.execute_script("arguments[0].click();", first)

    # 기존 호환용 — 자동완성 첫 항목 클릭으로 동작
    def has_results(self) -> bool:
        return self.has_autocomplete_results()

    def get_result_count(self) -> int:
        return self.get_autocomplete_count()

    def click_first_result(self) -> None:
        self.click_first_autocomplete()

    def select_sido(self, text: str) -> None:
        self.select_by_text(self.REGION_SIDO, text)

    def select_gugun(self, text: str) -> None:
        self.select_by_text(self.REGION_GUGUN, text)

    def is_no_result_shown(self) -> bool:
        return self.is_present(self.NO_RESULT_MSG, timeout=4)

    def is_map_loaded(self) -> bool:
        return self.is_present(self.MAP_CONTAINER, timeout=10)

    def is_detail_popup_open(self) -> bool:
        return self.is_visible(self.DETAIL_POPUP, timeout=4)

    def close_popup_if_present(self, wait: float = 2.0) -> None:
        """로그인 후 팝업 닫기. wait(초) 동안 팝업 대기 후 JS 클릭."""
        self.sleep(wait)
        try:
            locator = self._resolve(self.POPUP_CLOSE_BTN)
            btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(locator)
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            pass

    def close_detail_popup(self) -> None:
        if self.is_present(self.POPUP_CLOSE_BTN, timeout=2):
            self.click(self.POPUP_CLOSE_BTN)

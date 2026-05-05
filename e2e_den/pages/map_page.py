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
    LOGIN_BTN           = ("css", "a.gnb-account-link[href*='sso-login']")

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

    # ── 진료시간/날짜 필터 ────────────────────────────────────────────────────
    FILTER_TOGGLE_BTN   = ("css", "button.btn-filter-search")
    FILTER_SHEET        = ("css", ".filter-sheet-working")
    FILTER_HOUR_BTN     = ("css", ".hour-btn")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    _LOGIN_BTN_CSS = "a.gnb-account-link[href*='sso-login']"

    def _get_login_btn(self):
        try:
            host = self.driver.find_element(By.TAG_NAME, "company-gnb")
            return host.shadow_root.find_element(By.CSS_SELECTOR, self._LOGIN_BTN_CSS)
        except Exception:
            return None

    def is_login_btn_present(self, timeout: int = 9) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: self._get_login_btn() is not None
            )
            return True
        except Exception:
            return False

    def click_login_btn(self) -> None:
        if not self.is_login_btn_present(timeout=10):
            raise RuntimeError("로그인 버튼을 찾을 수 없습니다 (Shadow DOM 또는 이미 로그인 상태)")
        self.driver.execute_script("arguments[0].click();", self._get_login_btn())

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

    # ── 진료시간/날짜 필터 동작 ───────────────────────────────────────────────

    def open_working_time_filter(self) -> None:
        """아래 화살표 클릭으로 진료시간/날짜 필터 패널 열기"""
        self.driver.execute_script(
            "var btn = document.querySelector('i.icon-arrow-down.size-20');"
            "if (btn) btn.closest('button').click();"
        )
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".filter-sheet-working"))
        )
        self.sleep(1)  # 달력 내부 스팬 렌더링 대기

    def close_working_time_filter(self) -> None:
        """필터 토글 버튼 재클릭으로 진료시간/날짜 패널 닫기"""
        self.driver.execute_script(
            "var btn = document.querySelector('button.btn-filter-search');"
            "if (btn) btn.click();"
        )
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".filter-sheet-working"))
        )

    def select_hour(self, hour_text: str) -> None:
        """진료 시간 버튼 클릭 (예: '17:00') — JS로 직접 처리해 StaleElement 회피"""
        clicked = self.driver.execute_script("""
            var btns = document.querySelectorAll('.hour-btn');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent.trim() === arguments[0]) {
                    btns[i].click();
                    return true;
                }
            }
            return false;
        """, hour_text)
        if not clicked:
            raise ValueError("시간 버튼 '{0}'를 찾을 수 없음".format(hour_text))
        self.sleep(0.3)

    def select_date_by_day(self, day: int) -> None:
        """달력에서 활성화된 날짜 클릭 (disabled·other-month 제외)"""
        clicked = self.driver.execute_script("""
            var target = String(arguments[0]);
            var spans = document.querySelectorAll('.schedule-wrap span');
            for (var i = 0; i < spans.length; i++) {
                var s = spans[i];
                if (s.textContent.trim() === target
                    && !s.classList.contains('disabled')
                    && !s.classList.contains('other-month')) {
                    var label = s.closest('label');
                    if (label) { label.click(); return true; }
                }
            }
            return false;
        """, day)
        if not clicked:
            raise ValueError("날짜 '{0}'를 클릭할 수 없음 (비활성화 또는 없음)".format(day))
        self.sleep(0.3)

    def get_filter_btn_text(self) -> str:
        """필터 버튼에 표시된 진료시간/날짜 텍스트 반환"""
        return self.find(self.FILTER_TOGGLE_BTN, timeout=5).text.strip()

    def select_hour_range(self, start_hour: str, end_hour: str) -> None:
        """시작~종료 시간 범위의 모든 시간 버튼 클릭 (예: '00:00', '13:00')"""
        start_h = int(start_hour.split(":")[0])
        end_h = int(end_hour.split(":")[0])
        for h in range(start_h, end_h + 1):
            hour_str = "{0:02d}:00".format(h)
            clicked = self.driver.execute_script("""
                var btns = document.querySelectorAll('.hour-btn');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim() === arguments[0]) {
                        btns[i].click();
                        return true;
                    }
                }
                return false;
            """, hour_str)
            if not clicked:
                raise ValueError("시간 버튼 '{0}'를 찾을 수 없음".format(hour_str))
            self.sleep(0.1)

    def get_filter_month(self):
        """현재 달력 레이블(예: '2026.05')에서 (year, month) 반환"""
        label = self.find(("css", ".month-nav-label"), timeout=5).text.strip()
        parts = label.split(".")
        return int(parts[0]), int(parts[1])

    def navigate_filter_to_month(self, target_year: int, target_month: int) -> None:
        """달력을 target_year/target_month까지 < > 버튼으로 이동 (최대 36개월)"""
        for _ in range(36):
            cur_year, cur_month = self.get_filter_month()
            if cur_year == target_year and cur_month == target_month:
                return
            cur_total = cur_year * 12 + cur_month
            tgt_total = target_year * 12 + target_month
            if tgt_total < cur_total:
                self.driver.execute_script(
                    "var btn = document.querySelector('i.icon-arrow-left.size-12');"
                    "if (btn) btn.closest('button').click();"
                )
            else:
                self.driver.execute_script(
                    "var btn = document.querySelector('i.icon-arrow-right.size-12');"
                    "if (btn) btn.closest('button').click();"
                )
            self.sleep(0.5)
        raise ValueError("달력을 {0}-{1:02d}으로 이동할 수 없음".format(target_year, target_month))

    def select_date(self, year: int, month: int, day: int) -> None:
        """달력을 해당 연/월로 이동한 뒤 날짜 클릭"""
        self.navigate_filter_to_month(year, month)
        self.select_date_by_day(day)

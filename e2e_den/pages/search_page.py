"""
SearchPage - 사이트 전역 검색 페이지 엘리먼트 및 동작 정의
대상: https://osstem.com/desktop 검색 기능
"""

from pages.base_page import BasePage


class SearchPage(BasePage):

    # ── 검색 입력 영역 (GNB 검색) ─────────────────────────────────────────────
    SEARCH_INPUT    = ("css", "input[type='search'], input[name='q'], "
                              "input[name='search'], input[placeholder*='검색']")
    SEARCH_BTN      = ("css", "button[type='submit'], .btn-search, "
                              "[class*='search'][class*='btn']")
    SEARCH_ICON     = ("css", ".search-icon, .icon-search, [class*='search'][class*='icon']")

    # ── 검색 결과 ─────────────────────────────────────────────────────────────
    RESULT_LIST     = ("css", ".search-result, .result-list, [class*='result'][class*='list']")
    RESULT_ITEM     = ("css", ".result-item, .search-item, [class*='result'][class*='item']")
    RESULT_COUNT    = ("css", ".result-count, .total-count, [class*='count']")
    NO_RESULT_MSG   = ("css", ".no-result, .no-data, .empty, [class*='no-result']")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    def open_search(self) -> None:
        """검색창이 숨겨진 경우 아이콘 클릭으로 열기"""
        if self.is_present(self.SEARCH_ICON, timeout=3):
            self.click(self.SEARCH_ICON)

    def search(self, keyword: str) -> None:
        try:
            self.open_search()
            self.type_text(self.SEARCH_INPUT, keyword)
            self.click(self.SEARCH_BTN)
        except Exception as e:
            self.screenshot("search_fail")
            raise RuntimeError("검색 동작 실패: {0}".format(e))

    def search_with_enter(self, keyword: str) -> None:
        self.open_search()
        self.type_text(self.SEARCH_INPUT, keyword)
        self.press_key(self.SEARCH_INPUT, "ENTER")

    def get_result_count(self) -> int:
        return len(self.find_all(self.RESULT_ITEM))

    def has_results(self) -> bool:
        return self.get_result_count() > 0

    def get_result_texts(self) -> list:
        return self.get_texts(self.RESULT_ITEM)

    def is_no_result_shown(self) -> bool:
        return self.is_present(self.NO_RESULT_MSG, timeout=4)

    def clear_search(self) -> None:
        self.clear_field(self.SEARCH_INPUT)

    def close_search(self) -> None:
        """열린 검색창 닫기 (Escape 또는 닫기 버튼)"""
        try:
            if self.is_present(self.SEARCH_INPUT, timeout=2):
                self.press_key(self.SEARCH_INPUT, "ESCAPE")
        except Exception:
            pass

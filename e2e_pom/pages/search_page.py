"""
SearchPage - 검색 페이지 엘리먼트 및 동작 정의
"""

from pages.base_page import BasePage


class SearchPage(BasePage):

    # ── 엘리먼트 ─────────────────────────────────────────────────────────────
    SEARCH_INPUT  = ("css", "input.patientName__input")
    SEARCH_BTN    = ("css", "button[type='submit']")
    RESULT_ITEM   = ("id", "pt-nm")
    NO_RESULT_MSG = ("class", "no-results")
    PATIENT_INFO  = ("css", "div.patientInfo")

    # ── 동작 ─────────────────────────────────────────────────────────────────
    def search(self, keyword: str) -> None:
        try:
            self.type_text(self.SEARCH_INPUT, keyword)
            self.click(self.SEARCH_BTN)
        except Exception as e:
            self.screenshot("search_fail")
            raise RuntimeError("검색 동작 실패: {0}".format(e))

    def get_result_count(self) -> int:
        return len(self.find_all(self.RESULT_ITEM))

    def has_results(self) -> bool:
        return self.get_result_count() > 0

    def get_result_texts(self):
        return self.get_texts(self.RESULT_ITEM)

    def is_no_result_shown(self) -> bool:
        return self.is_present(self.NO_RESULT_MSG, timeout=3)

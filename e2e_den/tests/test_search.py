"""
test_search.py - 검색 시나리오 테스트
대상: https://osstem.com/desktop/map 검색 기능 (자동완성 드롭다운 #ac-listbox)
"""

import calendar
import pytest
from datetime import date, timedelta
from pages.map_page import MapPage

MAP_URL = "https://osstem.com/desktop/map"


def _future_day(days_ahead: int) -> int:
    """오늘로부터 days_ahead일 후 날짜(일). 다음 달로 넘어가면 이번 달 말일 반환."""
    today = date.today()
    target = today + timedelta(days=days_ahead)
    if target.month == today.month:
        return target.day
    return calendar.monthrange(today.year, today.month)[1]


@pytest.fixture
def search_page(logged_in_browser):
    """세션 브라우저로 지도(검색) 페이지 이동 (재로그인 없이 URL만 이동)."""
    page = MapPage(logged_in_browser)
    page.navigate(MAP_URL)
    page.close_popup_if_present()
    page.sleep(2)
    yield page
    # page.sleep(3)


class TestSearch:

    def test_검색창_존재(self, search_page):
        """검색 입력창이 페이지에 존재해야 함."""
        assert search_page.is_present(search_page.SEARCH_INPUT, timeout=5), \
            "검색 입력창이 존재해야 함"

    def test_유효한_키워드_자동완성_노출(self, search_page):
        """유효한 키워드 입력 시 자동완성 드롭다운에 결과가 노출되어야 함."""
        if not search_page.is_present(search_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        search_page.type_search("서울")
        assert search_page.has_autocomplete_results(), \
            "유효한 키워드 입력 시 자동완성 결과가 1개 이상 노출되어야 함"

    def test_없는_키워드_결과_없음(self, search_page):
        """존재하지 않는 키워드 입력 시 자동완성 결과가 없어야 함."""
        if not search_page.is_present(search_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        search_page.type_text(search_page.SEARCH_INPUT, "zzzzz없는키워드zzzzz9999")
        search_page.sleep(2)
        count = search_page.get_autocomplete_count()
        assert count == 0 or search_page.is_no_result_shown(), \
            "없는 키워드 입력 시 자동완성 결과가 없어야 함"

    def test_특수문자_검색_처리(self, search_page):
        """특수문자 입력 시 오류 없이 처리되어야 함."""
        if not search_page.is_present(search_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        try:
            search_page.type_text(search_page.SEARCH_INPUT, "<script>alert(1)</script>")
            search_page.sleep(1)
            assert search_page.get_title() != "", "특수문자 입력 후 페이지가 정상이어야 함"
        except Exception as e:
            pytest.fail("특수문자 검색 시 예외 발생: {0}".format(e))

    def test_빈_키워드_검색(self, search_page):
        """빈 검색어 엔터 시 오류 없이 처리되어야 함."""
        if not search_page.is_present(search_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        try:
            search_page.click(search_page.SEARCH_INPUT)
            search_page.press_key(search_page.SEARCH_INPUT, "ENTER")
            search_page.sleep(1)
            assert search_page.get_title() != "", "빈 검색어 엔터 후 페이지가 정상이어야 함"
        except Exception as e:
            pytest.fail("빈 검색어 처리 시 예외 발생: {0}".format(e))

    def test_자동완성_항목_병원명_존재(self, search_page):
        """자동완성 결과 항목에 병원명 텍스트가 있어야 함."""
        if not search_page.is_present(search_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        search_page.type_search("서울")
        if not search_page.has_autocomplete_results():
            pytest.skip("자동완성 결과가 없음")
        names = search_page.get_autocomplete_names()
        assert len(names) > 0, "자동완성 항목에 병원명이 있어야 함"
        assert all(name != "" for name in names), "병원명이 빈 문자열이면 안 됨"

    def test_첫번째_결과_클릭(self, search_page):
        """자동완성 첫 번째 항목 클릭 시 지도가 반응해야 함."""
        if not search_page.is_present(search_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        search_page.type_search("서울")
        if not search_page.has_autocomplete_results():
            pytest.skip("자동완성 결과가 없어 클릭 테스트 생략")
        names = search_page.get_autocomplete_names()
        search_page.click_first_autocomplete()
        search_page.sleep(2)
        assert search_page.get_title() != "", \
            "첫 번째 자동완성 항목({0}) 클릭 후 페이지가 정상이어야 함".format(
                names[0] if names else "unknown"
            )


class TestWorkingTimeFilter:
    """진료시간 필터 — 시간/날짜 선택 후 버튼 표시 확인

    오늘 날짜 기준 과거 시간은 UI에 노출되지 않으므로
    시간 선택 전 미래 날짜를 먼저 선택해 24시간 전체를 활성화한다.
    """

    SELECT_HOUR_1 = "17:00"
    SELECT_DATE_2 = _future_day(10)
    SELECT_HOUR_3 = "16:00"
    SELECT_DATE_3 = _future_day(15)
    # 다음 달로 넘어간 날짜 그대로 사용 시 아래 변수로 교체 후 select_date(d.year, d.month, d.day) 방식으로 변경
    _FULL_DATE_2 = date.today() + timedelta(days=10)
    _FULL_DATE_3 = date.today() + timedelta(days=15)

    def test_진료시간_선택_후_표시_확인(self, search_page):
        """아래 화살표 클릭 → 미래 날짜로 시간 활성화 → 시간 선택 → 닫기 → 선택 시간이 표시되어야 함."""
        search_page.open_working_time_filter()
        # [날짜 선택 방식 전환] 아래 두 줄 중 하나만 활성화. 전환 시: 현재 활성 줄 주석 처리 + 주석된 줄 주석 해제
        search_page.select_date_by_day(self.SELECT_DATE_2)           # 이번 달 말일 대체 방식
        # d = self._FULL_DATE_2; search_page.select_date(d.year, d.month, d.day)  # 다음 달 넘어간 날짜 그대로 사용 시
        search_page.sleep(0.7)
        search_page.select_hour(self.SELECT_HOUR_1)
        search_page.close_working_time_filter()
        label = search_page.get_filter_btn_text()
        assert self.SELECT_HOUR_1 in label, \
            "선택한 시간 '{0}'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                self.SELECT_HOUR_1, label)

    def test_날짜_선택_후_표시_확인(self, search_page):
        """아래 화살표 클릭 → 날짜 선택 → 닫기 → 선택 날짜가 필터 버튼에 표시되어야 함."""
        search_page.open_working_time_filter()
        # [날짜 선택 방식 전환] 아래 두 줄 중 하나만 활성화. 전환 시: 현재 활성 줄 주석 처리 + 주석된 줄 주석 해제
        search_page.select_date_by_day(self.SELECT_DATE_2)           # 이번 달 말일 대체 방식
        # d = self._FULL_DATE_2; search_page.select_date(d.year, d.month, d.day)  # 다음 달 넘어간 날짜 그대로 사용 시
        search_page.close_working_time_filter()
        label = search_page.get_filter_btn_text()
        assert "{0}일".format(self.SELECT_DATE_2) in label, \
            "선택한 날짜 '{0}일'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                self.SELECT_DATE_2, label)

    def test_진료시간_날짜_모두_선택_후_표시_확인(self, search_page):
        """아래 화살표 클릭 → 날짜 먼저 선택(24시간 활성화) → 시간 선택 → 닫기 → 모두 표시되어야 함."""
        search_page.open_working_time_filter()
        # [날짜 선택 방식 전환] 아래 두 줄 중 하나만 활성화. 전환 시: 현재 활성 줄 주석 처리 + 주석된 줄 주석 해제
        search_page.select_date_by_day(self.SELECT_DATE_3)           # 이번 달 말일 대체 방식
        # d = self._FULL_DATE_3; search_page.select_date(d.year, d.month, d.day)  # 다음 달 넘어간 날짜 그대로 사용 시
        search_page.sleep(0.7)
        search_page.select_hour(self.SELECT_HOUR_3)
        search_page.close_working_time_filter()
        label = search_page.get_filter_btn_text()
        assert self.SELECT_HOUR_3 in label, \
            "선택한 시간 '{0}'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                self.SELECT_HOUR_3, label)
        assert "{0}일".format(self.SELECT_DATE_3) in label, \
            "선택한 날짜 '{0}일'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                self.SELECT_DATE_3, label)

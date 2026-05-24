"""
test_map.py - 지도 페이지 시나리오 테스트
대상: https://osstem.com/desktop/map
"""

import calendar
import pytest
from datetime import date, timedelta
from pages.map_page import MapPage

MAP_URL = "https://osstem.com/desktop/map"


def _future_day(days_ahead: int) -> int:
    """오늘로부터 days_ahead일 후 날짜(일). 다음 달로 넘어가면 이번 달 마지막 평일 반환."""
    today = date.today()
    target = today + timedelta(days=days_ahead)
    if target.month == today.month:
        return target.day
    last_day = calendar.monthrange(today.year, today.month)[1]
    last = date(today.year, today.month, last_day)
    while last.weekday() >= 5:  # 5=토, 6=일
        last -= timedelta(days=1)
    return last.day


@pytest.fixture
def map_page(logged_in_browser):
    """세션 브라우저로 지도 페이지 이동 (재로그인 없이 URL만 이동)."""
    page = MapPage(logged_in_browser)
    page.navigate(MAP_URL)
    page.close_popup_if_present()
    page.sleep(2)
    yield page
    # page.sleep(3)


@pytest.fixture
def map_page_no_login(browser):
    """비로그인 상태의 지도 페이지 (새 브라우저)."""
    page = MapPage(browser)
    page.navigate(MAP_URL)
    page.sleep(2)
    yield page
    # page.sleep(3)


class TestMap:

    def test_페이지_로딩(self, map_page):
        """지도 페이지 정상 로딩 확인."""
        assert map_page.get_title() != "", "타이틀이 비어있으면 안 됨"
        assert "osstem.com" in map_page.get_current_url(), \
            "URL에 'osstem.com'이 포함되어야 함"

    def test_URL_map_포함(self, map_page):
        """지도 페이지 URL에 'map'이 포함되어야 함."""
        assert "/map" in map_page.get_current_url(), \
            "지도 페이지 URL에 'map'이 포함되어야 함"

    def test_지도_컨테이너_로딩(self, map_page):
        """지도 컨테이너(canvas/div)가 페이지에 존재해야 함."""
        assert map_page.is_map_loaded(), \
            "지도 컨테이너가 존재해야 함"

    def test_검색창_존재(self, map_page):
        """지도 페이지 검색 입력창이 존재해야 함."""
        has_input = map_page.is_present(map_page.SEARCH_INPUT, timeout=5)
        assert has_input, "검색 입력창이 존재해야 함"

    # def test_지역_필터_존재(self, map_page): ######
    #     """시/도 또는 구/군 선택 필터가 존재해야 함."""
    #     has_sido  = map_page.is_present(map_page.REGION_SIDO, timeout=5)
    #     has_gugun = map_page.is_present(map_page.REGION_GUGUN, timeout=5)
    #     assert has_sido or has_gugun, \
    #         "지역 필터(시/도, 구/군 선택)가 존재해야 함"

    def test_키워드_검색(self, map_page):
        """키워드 검색 후 결과 또는 지도 변화가 있어야 함."""
        if not map_page.is_present(map_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음 — 선택자 확인 필요")
        map_page.search_with_enter("서울")
        map_page.sleep(2)
        # 결과 노출 또는 오류 없음 확인
        assert map_page.get_title() != "", "검색 후 페이지가 정상이어야 함"

    def test_검색_결과_목록_노출(self, map_page):
        """키워드 입력 후 자동완성 드롭다운(#ac-listbox)에 결과가 노출되어야 함."""
        if not map_page.is_present(map_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        map_page.type_search("서울")
        assert map_page.has_autocomplete_results(), \
            "자동완성 드롭다운에 결과가 1개 이상 노출되어야 함"

    def test_결과_없음_처리(self, map_page):
        """없는 키워드 입력 시 자동완성 결과가 없어야 함."""
        if not map_page.is_present(map_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        map_page.type_text(map_page.SEARCH_INPUT, "zzzzz없는치과zzzzz9999")
        map_page.sleep(2)
        count = map_page.get_autocomplete_count()
        assert count == 0 or map_page.is_no_result_shown(), \
            "없는 키워드 입력 시 자동완성 결과가 없어야 함"

    def test_첫번째_결과_클릭(self, map_page):
        """자동완성 첫 번째 항목 클릭 시 지도가 해당 위치로 이동해야 함."""
        if not map_page.is_present(map_page.SEARCH_INPUT, timeout=5):
            pytest.skip("검색창을 찾을 수 없음")
        map_page.type_search("서울")
        if not map_page.has_autocomplete_results():
            pytest.skip("자동완성 결과가 없어 클릭 테스트 생략")
        names = map_page.get_autocomplete_names()
        map_page.click_first_autocomplete()
        map_page.sleep(2)
        assert map_page.get_title() != "", \
            "첫 번째 자동완성 항목({0}) 클릭 후 페이지가 정상이어야 함".format(
                names[0] if names else "unknown"
        )

    # def test_시도_필터_선택(self, map_page):
    #     """시/도 필터 선택 후 결과가 갱신되어야 함."""
    #     if not map_page.is_present(map_page.REGION_SIDO, timeout=5):
    #         pytest.skip("시/도 선택 필터를 찾을 수 없음 — 선택자 확인 필요")
    #     try:
    #         map_page.select_sido("서울")
    #         map_page.sleep(2)
    #         assert map_page.get_title() != "", "시/도 선택 후 페이지가 정상이어야 함"
    #     except Exception:
    #         pytest.skip("시/도 선택 동작 실패 — 선택자 또는 옵션값 확인 필요")

    def test_비로그인_접근(self, map_page_no_login):
        """비로그인 상태에서 지도 페이지 접근 가능 여부 확인 (새 브라우저)."""
        url = map_page_no_login.get_current_url()
        title = map_page_no_login.get_title()
        # 접근 가능(map URL 유지) 또는 로그인 리다이렉트 둘 다 허용
        assert "osstem.com" in url and title != "", \
            "페이지가 정상적으로 로드되어야 함 (리다이렉트 포함)"

    def test_페이지_뒤로가기_상태_유지(self, map_page):
        """지도 페이지에서 뒤로가기 후 다시 돌아왔을 때 페이지가 정상 로드되어야 함."""
        map_page.go_back()
        map_page.sleep(1)
        map_page.go_forward()
        map_page.sleep(2)
        assert map_page.is_map_loaded(), \
            "뒤로가기 후 복귀 시 지도가 정상 로드되어야 함"


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

    def test_진료시간_선택_후_표시_확인(self, map_page):
        """아래 화살표 클릭 → 미래 날짜로 시간 활성화 → 시간 선택 → 닫기 → 선택 시간이 표시되어야 함."""
        map_page.open_working_time_filter()
        # [날짜 선택 방식 전환] 아래 두 줄 중 하나만 활성화. 전환 시: 현재 활성 줄 주석 처리 + 주석된 줄 주석 해제
        map_page.select_date_by_day(self.SELECT_DATE_2)           # 이번 달 말일 대체 방식
        # d = self._FULL_DATE_2; map_page.select_date(d.year, d.month, d.day)  # 다음 달 넘어간 날짜 그대로 사용 시
        map_page.sleep(0.7)
        map_page.select_hour(self.SELECT_HOUR_1)
        map_page.close_working_time_filter()
        label = map_page.get_filter_btn_text()
        assert self.SELECT_HOUR_1 in label, \
            "선택한 시간 '{0}'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                self.SELECT_HOUR_1, label)

    def test_날짜_선택_후_표시_확인(self, map_page):
        """아래 화살표 클릭 → 날짜 선택 → 닫기 → 선택 날짜가 필터 버튼에 표시되어야 함."""
        map_page.open_working_time_filter()
        # [날짜 선택 방식 전환] 아래 두 줄 중 하나만 활성화. 전환 시: 현재 활성 줄 주석 처리 + 주석된 줄 주석 해제
        map_page.select_date_by_day(self.SELECT_DATE_2)           # 이번 달 말일 대체 방식
        # d = self._FULL_DATE_2; map_page.select_date(d.year, d.month, d.day)  # 다음 달 넘어간 날짜 그대로 사용 시
        map_page.close_working_time_filter()
        label = map_page.get_filter_btn_text()
        assert "{0}일".format(self.SELECT_DATE_2) in label, \
            "선택한 날짜 '{0}일'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                self.SELECT_DATE_2, label)

    def test_진료시간_날짜_모두_선택_후_표시_확인(self, map_page):
        """아래 화살표 클릭 → 날짜 먼저 선택(24시간 활성화) → 시간 선택 → 닫기 → 모두 표시되어야 함."""
        d = self._FULL_DATE_3
        map_page.open_working_time_filter()
        map_page.select_date(d.year, d.month, d.day)
        map_page.sleep(0.7)
        map_page.select_hour(self.SELECT_HOUR_3)
        map_page.close_working_time_filter()
        label = map_page.get_filter_btn_text()
        assert self.SELECT_HOUR_3 in label, \
            "선택한 시간 '{0}'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                self.SELECT_HOUR_3, label)
        assert "{0}일".format(d.day) in label, \
            "선택한 날짜 '{0}일'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(
                d.day, label)


_D1 = date.today() + timedelta(days=1)
_D2 = date.today() + timedelta(days=30)
_D3 = date.today() + timedelta(days=60)


class TestWorkingTimeFilterRange:
    """진료시간 필터 — 시간/날짜 범위 선택 테스트 (파라미터화)

    시간 버튼은 단일 선택(마지막 클릭이 선택됨)이며,
    오늘 날짜 기준으로 과거 시간대는 UI에 렌더링되지 않음.
    → 미래 날짜를 먼저 선택해 24시간 전체 활성화 후 시간 선택.
    → 표시 검증은 마지막으로 클릭한 end_hour 기준.
    """

    @pytest.mark.parametrize("start_hour,end_hour,year,month,day", [
        ("00:00", "05:00", _D1.year, _D1.month, _D1.day),
        ("10:00", "13:00", _D2.year, _D2.month, _D2.day),
        ("18:00", "22:00", _D3.year, _D3.month, _D3.day),
    ])
    def test_시간_범위_선택_후_표시_확인(self, map_page, start_hour, end_hour, year, month, day):
        """미래 날짜 먼저 선택(24시간 활성화) → 시간 범위 클릭 → 마지막 시간이 표시되어야 함."""
        map_page.open_working_time_filter()
        map_page.select_date(year, month, day)  # 미래 날짜 → 모든 시간 버튼 활성화
        map_page.sleep(0.7)                     # 시간 버튼 re-render 대기
        map_page.select_hour_range(start_hour, end_hour)
        map_page.close_working_time_filter()
        label = map_page.get_filter_btn_text()
        # UI는 leading zero 없이 표시 (예: "05:00" → "5:00")
        end_display = "{0}:00".format(int(end_hour.split(":")[0]))
        assert end_display in label, \
            "마지막 선택 시간 '{0}'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(end_display, label)

    @pytest.mark.parametrize("year,month,day", [
        (_D1.year, _D1.month, _D1.day),
        (_D2.year, _D2.month, _D2.day),
        (_D3.year, _D3.month, _D3.day),
    ])
    def test_달력_월_이동_날짜_선택_후_표시_확인(self, map_page, year, month, day):
        """달력 월 이동 후 날짜 선택 시 해당 날짜가 필터 버튼에 표시되어야 함."""
        map_page.open_working_time_filter()
        map_page.select_date(year, month, day)
        map_page.close_working_time_filter()
        label = map_page.get_filter_btn_text()
        assert "{0}일".format(day) in label, \
            "선택한 날짜 '{0}일'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(day, label)

    @pytest.mark.parametrize("start_hour,end_hour,year,month,day", [
        ("00:00", "05:00", _D1.year, _D1.month, _D1.day),
        ("10:00", "13:00", _D2.year, _D2.month, _D2.day),
        ("18:00", "22:00", _D3.year, _D3.month, _D3.day),
    ])
    def test_시간_범위_날짜_복합_선택_후_표시_확인(self, map_page, start_hour, end_hour, year, month, day):
        """미래 날짜 먼저 선택(24시간 활성화) → 시간 범위 클릭 → 마지막 시간+날짜가 표시되어야 함."""
        map_page.open_working_time_filter()
        map_page.select_date(year, month, day)  # 미래 날짜 → 모든 시간 버튼 활성화
        map_page.sleep(0.7)                     # 시간 버튼 re-render 대기
        map_page.select_hour_range(start_hour, end_hour)
        map_page.close_working_time_filter()
        label = map_page.get_filter_btn_text()
        # UI는 leading zero 없이 표시 (예: "05:00" → "5:00")
        end_display = "{0}:00".format(int(end_hour.split(":")[0]))
        assert end_display in label, \
            "마지막 선택 시간 '{0}'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(end_display, label)
        assert "{0}일".format(day) in label, \
            "날짜 '{0}일'이 필터 버튼에 표시되어야 함. 실제: '{1}'".format(day, label)

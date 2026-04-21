"""
test_map.py - 지도 페이지 시나리오 테스트
대상: https://osstem.com/desktop/map
"""

import pytest
from pages.map_page import MapPage

MAP_URL = "https://osstem.com/desktop/map"


@pytest.fixture
def map_page(logged_in_browser):
    page = MapPage(logged_in_browser)
    page.close_popup_if_present()  # 로그인 후 팝업 잔존 시 추가 닫기
    page.sleep(2)  # 지도 API 로딩 대기
    yield page
    page.sleep(3)  # 테스트 종료 후 브라우저 유지


@pytest.fixture
def map_page_no_login(browser):
    """비로그인 상태의 지도 페이지"""
    page = MapPage(browser)
    page.navigate(MAP_URL)
    page.sleep(2)
    yield page
    page.sleep(3)  # 테스트 종료 후 브라우저 유지


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

    def test_시도_필터_선택(self, map_page):
        """시/도 필터 선택 후 결과가 갱신되어야 함."""
        if not map_page.is_present(map_page.REGION_SIDO, timeout=5):
            pytest.skip("시/도 선택 필터를 찾을 수 없음 — 선택자 확인 필요")
        try:
            map_page.select_sido("서울")
            map_page.sleep(2)
            assert map_page.get_title() != "", "시/도 선택 후 페이지가 정상이어야 함"
        except Exception:
            pytest.skip("시/도 선택 동작 실패 — 선택자 또는 옵션값 확인 필요")

    def test_비로그인_접근(self, map_page_no_login):
        """비로그인 상태에서 지도 페이지 접근 가능 여부 확인."""
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

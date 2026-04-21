"""
test_search.py - 검색 시나리오 테스트
대상: https://osstem.com/desktop/map 검색 기능 (자동완성 드롭다운 #ac-listbox)
"""

import pytest
from pages.map_page import MapPage


@pytest.fixture
def search_page(logged_in_browser):
    page = MapPage(logged_in_browser)
    page.close_popup_if_present()
    page.sleep(2)
    yield page
    page.sleep(3)  # 테스트 종료 후 브라우저 유지


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

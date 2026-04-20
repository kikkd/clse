"""
test_search.py - 검색 시나리오 테스트
"""

import pytest
from pages.search_page import SearchPage

# SEARCH_URL = "https://example.com/search"


@pytest.fixture
def search_page(logged_in_browser):
    page = SearchPage(logged_in_browser)
    # page.navigate(SEARCH_URL)
    return page


class TestSearch:

    def test_키워드_검색_결과_존재(self, search_page):
        """유효한 키워드 검색 시 결과 노출 확인."""
        search_page.search("python")
        assert search_page.has_results(), \
            "검색 결과가 1개 이상 있어야 함"

    def test_검색_결과_개수(self, search_page):
        """검색 결과 개수 확인."""
        search_page.search("python")
        count = search_page.get_result_count()
        assert count >= 1, "결과가 {0}개 — 1개 이상이어야 함".format(count)

    def test_빈_키워드_검색(self, search_page):
        """빈 키워드 검색 시 결과 없음 메시지 확인."""
        search_page.search("")
        assert search_page.is_no_result_shown() or not search_page.has_results(), \
            "빈 검색어는 결과가 없어야 함"

    def test_존재하지_않는_키워드(self, search_page):
        """없는 키워드 검색 시 결과 없음 확인."""
        search_page.search("zzzzz_없는키워드_zzzzz")
        assert search_page.is_no_result_shown() or not search_page.has_results(), \
            "없는 키워드는 결과가 없어야 함"

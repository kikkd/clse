"""
test_search.py - 검색 시나리오 테스트
"""

import pytest
from selenium.webdriver.support.ui import WebDriverWait
from pages.search_page import SearchPage

# SEARCH_URL = "https://hippo2qa.osstem.com/web/9138b3f884f9921a5b615c704589dda44cdf7bb7988a24a4b488c0caa71d544c/hippo/desk"


@pytest.fixture
def search_page(logged_in_browser):
    page = SearchPage(logged_in_browser)
    current_url = page.get_current_url()
    new_url = current_url[:current_url.rfind('/') + 1] + 'desk' #기본 랜딩 페이지에서 데스크로 이동
    page.navigate(new_url)
    # page.navigate(SEARCH_URL)
    return page


class TestSearch:
    def test_키워드_차트번호_검색_결과_존재(self, search_page):
        """유효한 키워드 검색 시 결과 노출 확인."""
        keyword = "3"
        search_page.type_text(SearchPage.SEARCH_INPUT, keyword)
        search_page.press_key(SearchPage.SEARCH_INPUT, "ENTER")
        element = search_page.find(SearchPage.PATIENT_INFO)
        WebDriverWait(search_page.driver, 10).until(
            lambda d: d.execute_script("return arguments[0].innerText;", element).strip() != ""
        )
        patient_text = search_page.driver.execute_script("return arguments[0].innerText;", element).strip()
        assert patient_text.startswith(keyword), \
            "환자 정보 '{0}'가 검색어 '{1}'로 시작해야 함".format(patient_text, keyword)
        
    def test_키워드_환자이름_검색_결과_존재(self, search_page):
        """유효한 키워드 검색 시 결과 노출 확인."""
        keyword = "최규천"
        search_page.type_text(SearchPage.SEARCH_INPUT, keyword)
        search_page.press_key(SearchPage.SEARCH_INPUT, "ENTER")
        element = search_page.find(("id", "pt-nm"))
        WebDriverWait(search_page.driver, 10).until(
            lambda d: d.execute_script("return arguments[0].value;", element) != ""
        )
        patient_text = search_page.driver.execute_script("return arguments[0].value;", element)
        assert patient_text.startswith(keyword), \
            "환자 정보 '{0}'가 검색어 '{1}'로 시작해야 함".format(patient_text, keyword)
        
    # def test_검색_결과_개수(self, search_page):
    #     """검색 결과 개수 확인."""
    #     search_page.search("python")
    #     count = search_page.get_result_count()
    #     assert count >= 1, "결과가 {0}개 — 1개 이상이어야 함".format(count)

    # def test_빈_키워드_검색(self, search_page):
    #     """빈 키워드 검색 시 결과 없음 메시지 확인."""
    #     search_page.search("")
    #     assert search_page.is_no_result_shown() or not search_page.has_results(), \
    #         "빈 검색어는 결과가 없어야 함"

    # def test_존재하지_않는_키워드(self, search_page):
    #     """없는 키워드 검색 시 결과 없음 확인."""
    #     search_page.search("zzzzz_없는키워드_zzzzz")
    #     assert search_page.is_no_result_shown() or not search_page.has_results(), \
    #         "없는 키워드는 결과가 없어야 함"

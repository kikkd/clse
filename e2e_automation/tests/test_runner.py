"""
Test Runner - 엑셀 데이터 기반 E2E 테스트 실행기
URL과 브라우저를 입력받아 테스트를 실행하고 리포트를 생성한다.
"""

import time
import logging
import traceback

from drivers.browser_factory import create_driver
from pages.base_page import BasePage
from utils.excel_handler import load_sheet
from utils.reporter import Reporter, TestResult, STATUS_PASS, STATUS_FAIL

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────────────
# 공통 헬퍼
# ────────────────────────────────────────────────────────────────────────────

def _parse_nth(row, key="nth"):
    val = str(row.get(key, "")).strip()
    if val and val.isdigit() and int(val) >= 1:
        return int(val)
    return None


def _parse_wait(row, key="wait_before"):
    val = str(row.get(key, "")).strip()
    try:
        return float(val) if val else 0.0
    except ValueError:
        return 0.0


def _locator(row, prefix=""):
    lt = row.get("{0}locator_type".format(prefix), "").strip()
    lv = row.get("{0}locator_value".format(prefix), "").strip()
    if not lt or not lv:
        raise ValueError(
            "[{0}locator_type / {0}locator_value] 컬럼이 비어 있습니다.".format(prefix)
        )
    return (lt, lv)


def _pass(reporter, row, start, page, desc_default, shot):
    reporter.add(TestResult(
        test_id=row["test_id"],
        description=row.get("description", desc_default),
        status=STATUS_PASS,
        duration=round(time.time() - start, 2),
        url=page.get_current_url(),
        browser=row.get("_browser", ""),
        screenshot=shot,
    ))


def _fail(reporter, row, start, page_or_url, desc_default, shot, error):
    url = page_or_url if isinstance(page_or_url, str) else page_or_url.get_current_url()
    reporter.add(TestResult(
        test_id=row["test_id"],
        description=row.get("description", desc_default),
        status=STATUS_FAIL,
        duration=round(time.time() - start, 2),
        url=url,
        browser=row.get("_browser", ""),
        screenshot=shot,
        error_msg=str(error),
    ))


def _get_text(page, element):
    """
    element.text 가 빈 문자열이면 JS textContent 로 재시도.
    Vue / React 등 동적 렌더링 환경에서 .text 가 빈 값으로 오는 문제 대응.
    공백·줄바꿈을 정규화하여 반환.
    """
    text = element.text.strip()
    if not text:
        text = page.driver.execute_script(
            "return arguments[0].textContent;", element
        )
        if text:
            text = " ".join(text.split())  # 연속 공백·줄바꿈 정규화
    return text.strip()


def _do_click(page, row):
    """공통 클릭 동작: locator_type/locator_value/nth 읽어서 클릭."""
    loc = _locator(row)
    nth = _parse_nth(row)
    if nth:
        page.click_nth(loc, nth)
    else:
        page.click(loc)


def _do_verify(page, row):
    """
    공통 검증 동작: verify_locator_type/verify_locator_value/verify_nth 엘리먼트를
    verify_expect(present|absent|text) 방식으로 확인한다.
    """
    v_loc  = _locator(row, "verify_")
    v_nth  = _parse_nth(row, "verify_nth")
    expect = row.get("verify_expect", "present").strip().lower()

    if expect == "absent":
        # 엘리먼트가 없어야 PASS
        found = page.is_present(v_loc, timeout=5)
        if found:
            raise AssertionError(
                "엘리먼트가 사라지지 않음 | [{0}={1}]".format(
                    row.get("verify_locator_type", ""),
                    row.get("verify_locator_value", ""),
                )
            )

    elif expect == "text":
        # 엘리먼트 텍스트가 expected_text와 일치해야 PASS
        expected_text = row.get("expected_text", "").strip()
        element = page.find_nth(v_loc, v_nth) if v_nth else page.find(v_loc)
        actual  = _get_text(page, element)
        if actual != expected_text:
            raise AssertionError(
                "텍스트 불일치 | 예상: '{0}' | 실제: '{1}'".format(expected_text, actual)
            )

    else:
        # present (기본): 엘리먼트가 있어야 PASS
        if not page.is_present(v_loc):
            raise AssertionError(
                "엘리먼트 없음 | [{0}={1}]".format(
                    row.get("verify_locator_type", ""),
                    row.get("verify_locator_value", ""),
                )
            )


# ────────────────────────────────────────────────────────────────────────────
# 개별 테스트 타입 핸들러
# ────────────────────────────────────────────────────────────────────────────

def tc_page_load(page, url, row, reporter):
    """페이지 접속 후 타이틀 및 URL 확인."""
    start = time.time()
    try:
        page.navigate(url)
        assert page.get_title(), "페이지 타이틀이 비어 있음"
        expected_url = row.get("expected_url_contains", "").strip()
        if expected_url:
            page.wait_for_url_contains(expected_url)
        shot = page.screenshot("{0}_load".format(row["test_id"]))
        _pass(reporter, row, start, page, "페이지 로딩", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, url, "페이지 로딩", shot, e)


def tc_click(page, url, row, reporter):
    """엘리먼트 클릭."""
    start = time.time()
    try:
        page.navigate(url)
        wait = _parse_wait(row)
        if wait:
            time.sleep(wait)
        _do_click(page, row)
        expected_url = row.get("expected_url_contains", "").strip()
        if expected_url:
            page.wait_for_url_contains(expected_url)
        shot = page.screenshot("{0}_click".format(row["test_id"]))
        _pass(reporter, row, start, page, "클릭", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, page, "클릭",
              shot, "[{0}] {1}".format(row.get("locator_value", ""), e))


def tc_click_and_verify(page, url, row, reporter):
    """
    엘리먼트 클릭 후 다른 엘리먼트를 확인.

    클릭 컬럼 : locator_type | locator_value | nth | wait_before
    검증 컬럼 : verify_locator_type | verify_locator_value | verify_nth
    검증 방식 : verify_expect = present(기본) | absent | text
    텍스트 비교: expected_text  (verify_expect=text 일 때)
    클릭 후 대기: wait_after    (검증 전 UI 변화 대기, 초 단위)
    """
    start = time.time()
    try:
        page.navigate(url)

        wait_before = _parse_wait(row, "wait_before")
        if wait_before:
            time.sleep(wait_before)

        _do_click(page, row)

        wait_after = _parse_wait(row, "wait_after")
        if wait_after:
            time.sleep(wait_after)

        _do_verify(page, row)

        shot = page.screenshot("{0}_click_verify".format(row["test_id"]))
        _pass(reporter, row, start, page, "클릭 후 확인", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, page, "클릭 후 확인", shot, e)


def tc_input(page, url, row, reporter):
    """텍스트 입력만 (제출 없음)."""
    start = time.time()
    try:
        page.navigate(url)
        wait = _parse_wait(row)
        if wait:
            time.sleep(wait)
        loc = _locator(row)
        nth = _parse_nth(row)
        page.type_text(loc, row.get("input_text", ""), nth=nth)
        shot = page.screenshot("{0}_input".format(row["test_id"]))
        _pass(reporter, row, start, page, "텍스트 입력", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, url, "텍스트 입력", shot, e)


def tc_input_and_submit(page, url, row, reporter):
    """텍스트 입력 후 버튼 제출."""
    start = time.time()
    try:
        page.navigate(url)
        wait = _parse_wait(row)
        if wait:
            time.sleep(wait)
        in_loc     = _locator(row, "input_")
        sub_loc    = _locator(row, "submit_")
        input_nth  = _parse_nth(row, "input_nth")
        submit_nth = _parse_nth(row, "submit_nth")
        page.type_text(in_loc, row.get("input_text", ""), nth=input_nth)
        if submit_nth:
            page.click_nth(sub_loc, submit_nth)
        else:
            page.click(sub_loc)
        expected_url = row.get("expected_url_contains", "").strip()
        if expected_url:
            page.wait_for_url_contains(expected_url)
        shot = page.screenshot("{0}_submit".format(row["test_id"]))
        _pass(reporter, row, start, page, "입력 및 제출", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, url, "입력 및 제출", shot, e)


def tc_verify_text(page, url, row, reporter):
    """엘리먼트 텍스트 일치 확인."""
    start = time.time()
    try:
        page.navigate(url)
        wait = _parse_wait(row)
        if wait:
            time.sleep(wait)
        loc      = _locator(row)
        nth      = _parse_nth(row)
        expected = row.get("expected_text", "").strip()
        element  = page.find_nth(loc, nth) if nth else page.find(loc)
        actual   = _get_text(page, element)
        if actual != expected:
            raise AssertionError(
                "텍스트 불일치 | 예상: '{0}' | 실제: '{1}'".format(expected, actual)
            )
        shot = page.screenshot("{0}_verify".format(row["test_id"]))
        _pass(reporter, row, start, page, "텍스트 확인", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, url, "텍스트 확인", shot, e)


def tc_verify_present(page, url, row, reporter):
    """엘리먼트 존재 확인."""
    start = time.time()
    try:
        page.navigate(url)
        wait = _parse_wait(row)
        if wait:
            time.sleep(wait)
        loc = _locator(row)
        if not page.is_present(loc):
            raise AssertionError(
                "엘리먼트 없음 | [{0}={1}]".format(
                    row.get("locator_type", ""), row.get("locator_value", ""))
            )
        shot = page.screenshot("{0}_present".format(row["test_id"]))
        _pass(reporter, row, start, page, "엘리먼트 존재 확인", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, url, "엘리먼트 존재 확인", shot, e)


def tc_verify_url(page, url, row, reporter):
    """페이지 접속 후 URL에 expected_url_contains 포함 여부 확인."""
    start = time.time()
    try:
        expected = row.get("expected_url_contains", "").strip()
        if not expected:
            raise ValueError("expected_url_contains 컬럼이 비어 있습니다.")
        page.navigate(url)
        wait = _parse_wait(row)
        if wait:
            time.sleep(wait)
        page.wait_for_url_contains(expected)
        shot = page.screenshot("{0}_url".format(row["test_id"]))
        _pass(reporter, row, start, page, "URL 확인", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, url, "URL 확인", shot, e)


def tc_select(page, url, row, reporter):
    """드롭다운 선택 (select_by: text | value | index)."""
    start = time.time()
    try:
        page.navigate(url)
        wait = _parse_wait(row)
        if wait:
            time.sleep(wait)
        loc     = _locator(row)
        by      = row.get("select_by", "text").strip().lower()
        sel_val = row.get("select_value", "").strip()
        if by == "value":
            page.select_by_value(loc, sel_val)
        elif by == "index":
            page.select_by_index(loc, int(sel_val))
        else:
            page.select_by_text(loc, sel_val)
        shot = page.screenshot("{0}_select".format(row["test_id"]))
        _pass(reporter, row, start, page, "드롭다운 선택", shot)
    except Exception as e:
        shot = page.screenshot("{0}_fail".format(row["test_id"]))
        _fail(reporter, row, start, url, "드롭다운 선택", shot, e)


# ── 테스트 타입 → 핸들러 매핑 ──────────────────────────────────────────────
TEST_DISPATCHERS = {
    "page_load":          tc_page_load,
    "click":              tc_click,
    "click_and_verify":   tc_click_and_verify,
    "input":              tc_input,
    "input_and_submit":   tc_input_and_submit,
    "verify_text":        tc_verify_text,
    "verify_present":     tc_verify_present,
    "verify_url":         tc_verify_url,
    "select":             tc_select,
}


# ────────────────────────────────────────────────────────────────────────────
# 공통 실행 엔진
# ────────────────────────────────────────────────────────────────────────────

def _execute(rows, url, browser, reporter, page):
    for row in rows:
        row["_browser"] = browser
        test_type = row.get("test_type", "").strip()
        handler   = TEST_DISPATCHERS.get(test_type)
        if handler is None:
            logger.warning("알 수 없는 test_type: '{0}' → 스킵".format(test_type))
            continue
        try:
            handler(page, url, row, reporter)
        except Exception:
            logger.error(traceback.format_exc())


def _print_header(url, browser, sheet, suite_name):
    sep = "═" * 55
    print("\n{0}".format(sep))
    print("  {0}".format(suite_name))
    print("  URL     : {0}".format(url))
    print("  Browser : {0}".format(browser))
    print("  Sheet   : {0}".format(sheet))
    print("{0}\n".format(sep))


# ────────────────────────────────────────────────────────────────────────────
# 공개 실행 함수
# ────────────────────────────────────────────────────────────────────────────

def run_tests(url, browser="chrome", sheet_name="tests",
              excel_path=None, suite_name="E2E Test Suite"):
    # type: (str, str, str, str, str) -> Reporter
    reporter = Reporter(suite_name)
    _print_header(url, browser, sheet_name, suite_name)

    try:
        rows = load_sheet(sheet_name, excel_path)
    except FileNotFoundError as e:
        print("[ERROR] {0}".format(e))
        return reporter

    driver = create_driver(browser)
    try:
        _execute(rows, url, browser, reporter, BasePage(driver))
    finally:
        driver.quit()

    reporter.print_summary()
    json_path = reporter.save_json()
    html_path = reporter.save_html()
    print("\n  JSON 리포트 → {0}".format(json_path))
    print("  HTML 리포트 → {0}\n".format(html_path))
    return reporter


def run_suite(url, browser="chrome", sheet_name="test_suite",
              excel_path=None, suite_name="E2E Full Suite"):
    # type: (str, str, str, str, str) -> Reporter
    return run_tests(
        url=url,
        browser=browser,
        sheet_name=sheet_name,
        excel_path=excel_path,
        suite_name=suite_name,
    )

"""
UI Element Map - 모든 웹 엘리먼트를 딕셔너리로 모듈화 관리
By: (locator_type, locator_value) 형태로 저장
locator_type: id | name | xpath | css | class | tag | link_text | partial_link_text
"""

from selenium.webdriver.common.by import By

# ── 공통 Locator 유형 매핑 ──────────────────────────────────────────────────
LOCATOR_TYPES = {
    "id":               By.ID,
    "name":             By.NAME,
    "xpath":            By.XPATH,
    "css":              By.CSS_SELECTOR,
    "class":            By.CLASS_NAME,
    "tag":              By.TAG_NAME,
    "link_text":        By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
}

# ── 공통 엘리먼트 (모든 사이트 공통) ──────────────────────────────────────────
COMMON_ELEMENTS = {
    "body":             ("tag",   "body"),
    "title":            ("tag",   "title"),
    "all_links":        ("tag",   "a"),
    "all_buttons":      ("tag",   "button"),
    "all_inputs":       ("tag",   "input"),
    "all_forms":        ("tag",   "form"),
}

# ── 로그인 관련 엘리먼트 ────────────────────────────────────────────────────
LOGIN_ELEMENTS = {
    "username_id":      ("id",    "username"),
    "username_name":    ("name",  "username"),
    "email_id":         ("id",    "email"),
    "password_id":      ("id",    "password"),
    "password_name":    ("name",  "password"),
    "login_btn_id":     ("id",    "login-btn"),
    "login_btn_xpath":  ("xpath", "//button[contains(text(),'Login') or contains(text(),'로그인')]"),
    "submit_btn":       ("xpath", "//button[@type='submit']"),
    "logout_link":      ("partial_link_text", "Logout"),
}

# ── 네비게이션 엘리먼트 ─────────────────────────────────────────────────────
NAV_ELEMENTS = {
    "nav_bar":          ("tag",   "nav"),
    "menu_items":       ("css",   "nav ul li a"),
    "home_link":        ("partial_link_text", "Home"),
    "search_input":     ("css",   "input[type='search'], input[name='q'], input[name='search']"),
    "search_btn":       ("css",   "button[type='submit'], input[type='submit']"),
}

# ── 폼 관련 엘리먼트 ─────────────────────────────────────────────────────────
FORM_ELEMENTS = {
    "text_inputs":      ("css",   "input[type='text']"),
    "email_inputs":     ("css",   "input[type='email']"),
    "password_inputs":  ("css",   "input[type='password']"),
    "checkboxes":       ("css",   "input[type='checkbox']"),
    "radio_buttons":    ("css",   "input[type='radio']"),
    "dropdowns":        ("tag",   "select"),
    "textareas":        ("tag",   "textarea"),
    "submit_buttons":   ("css",   "button[type='submit'], input[type='submit']"),
    "reset_buttons":    ("css",   "button[type='reset'], input[type='reset']"),
}

# ── 알림/메시지 엘리먼트 ─────────────────────────────────────────────────────
ALERT_ELEMENTS = {
    "success_msg":      ("css",   ".success, .alert-success, [class*='success']"),
    "error_msg":        ("css",   ".error, .alert-error, .alert-danger, [class*='error']"),
    "warning_msg":      ("css",   ".warning, .alert-warning, [class*='warning']"),
    "info_msg":         ("css",   ".info, .alert-info, [class*='info']"),
    "modal":            ("css",   ".modal, [role='dialog']"),
    "modal_close":      ("css",   ".modal .close, [data-dismiss='modal']"),
}

# ── 테이블/리스트 엘리먼트 ──────────────────────────────────────────────────
TABLE_ELEMENTS = {
    "table":            ("tag",   "table"),
    "table_rows":       ("css",   "table tbody tr"),
    "table_headers":    ("css",   "table thead th"),
    "table_cells":      ("css",   "table tbody td"),
    "pagination":       ("css",   ".pagination, [aria-label='pagination']"),
    "next_page":        ("css",   ".pagination .next, a[rel='next']"),
    "prev_page":        ("css",   ".pagination .prev, a[rel='prev']"),
}


def get_element(element_map: dict, key: str) -> tuple:
    """딕셔너리에서 엘리먼트 locator를 가져와 (By.TYPE, value) 형태로 반환"""
    if key not in element_map:
        raise KeyError(f"Element '{key}' not found in element map.")
    locator_type_str, locator_value = element_map[key]
    by = LOCATOR_TYPES.get(locator_type_str)
    if by is None:
        raise ValueError(f"Unknown locator type: '{locator_type_str}'")
    return (by, locator_value)


def get_all_maps() -> dict:
    """모든 엘리먼트 맵을 하나로 병합하여 반환"""
    return {
        **COMMON_ELEMENTS,
        **LOGIN_ELEMENTS,
        **NAV_ELEMENTS,
        **FORM_ELEMENTS,
        **ALERT_ELEMENTS,
        **TABLE_ELEMENTS,
    }

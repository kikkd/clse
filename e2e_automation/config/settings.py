import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BROWSER_OPTIONS = {
    "chrome": {
        "headless": False,
        "window_size": (1920, 1080),
        "disable_gpu": True,
        "no_sandbox": True,
    },
    "firefox": {
        "headless": False,
        "window_size": (1920, 1080),
    },
    "edge": {
        "headless": False,
        "window_size": (1920, 1080),
    },
    "safari": {
        "headless": False,
        "window_size": (1920, 1080),
    },
}

TIMEOUTS = {
    "implicit": 0,    # explicit wait과 충돌 방지 — 항상 0 유지
    "explicit": 10,   # 엘리먼트 대기 최대 10초
    "page_load": 30,  # 페이지 로딩 최대 30초
    "script": 15,
}

PATHS = {
    "data":    os.path.join(BASE_DIR, "data", "test_data.xlsx"),
    "reports": os.path.join(BASE_DIR, "reports"),
    "screenshots": os.path.join(BASE_DIR, "reports", "screenshots"),
}

SUPPORTED_BROWSERS = ["chrome", "firefox", "edge", "safari"]

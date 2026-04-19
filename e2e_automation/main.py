"""
E2E 자동화 진입점
실행: python main.py
"""

import sys
import logging
import argparse
import os

from config.settings import SUPPORTED_BROWSERS, PATHS
from utils.excel_handler import create_sample_excel, get_sheet_names
from tests.test_runner import run_tests, run_suite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="E2E 웹 자동화 테스트 실행기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python main.py                              # 대화형 입력
  python main.py -u https://example.com       # URL 지정
  python main.py -u https://example.com -b firefox -s login
  python main.py --init                       # 샘플 엑셀 생성
        """,
    )
    parser.add_argument("-u", "--url",     help="테스트 대상 URL")
    parser.add_argument("-b", "--browser", default="chrome",
                        choices=SUPPORTED_BROWSERS, help="브라우저 (기본: chrome)")
    parser.add_argument("-s", "--sheet",   default="tests", help="엑셀 시트 이름 (기본: tests)")
    parser.add_argument("-f", "--file",    help="엑셀 파일 경로 (기본: data/test_data.xlsx)")
    parser.add_argument("--suite",         default="E2E Test Suite", help="리포트 스위트 이름")
    parser.add_argument("--run-suite",     action="store_true", help="통합 시트(test_suite)로 전체 테스트 실행")
    parser.add_argument("--init",          action="store_true", help="샘플 엑셀 파일 생성 후 종료")
    parser.add_argument("--list-sheets",   action="store_true", help="엑셀 시트 목록 출력 후 종료")
    return parser.parse_args()


def prompt_url() -> str:
    while True:
        url = input("\n  테스트할 URL을 입력하세요 (예: https://example.com): ").strip()
        if url.startswith("http://") or url.startswith("https://"):
            return url
        print("  [!] URL은 http:// 또는 https://로 시작해야 합니다.")


def prompt_browser() -> str:
    print(f"\n  지원 브라우저: {', '.join(SUPPORTED_BROWSERS)}")
    browser = input("  브라우저를 입력하세요 (기본: chrome): ").strip().lower() or "chrome"
    if browser not in SUPPORTED_BROWSERS:
        print(f"  [!] 지원하지 않는 브라우저. chrome으로 실행합니다.")
        return "chrome"
    return browser


def prompt_sheet(excel_path: str) -> str:
    try:
        sheets = get_sheet_names(excel_path)
        print(f"\n  사용 가능한 시트: {', '.join(sheets)}")
        sheet = input("  시트 이름을 입력하세요 (기본: tests): ").strip() or "tests"
        if sheet not in sheets:
            print(f"  [!] '{sheet}' 시트 없음. 첫 번째 시트 '{sheets[0]}' 사용.")
            return sheets[0]
        return sheet
    except Exception:
        return "tests"


def main():
    args = parse_args()

    # ── 샘플 엑셀 생성 ────────────────────────────────────────────────────────
    if args.init:
        create_sample_excel(args.file)
        return

    # ── 시트 목록 출력 ────────────────────────────────────────────────────────
    if args.list_sheets:
        path = args.file or PATHS["data"]
        sheets = get_sheet_names(path)
        print(f"시트 목록 ({path}):")
        for s in sheets:
            print(f"  - {s}")
        return

    # ── 엑셀 파일 존재 확인 ───────────────────────────────────────────────────
    excel_path = args.file or PATHS["data"]
    if not os.path.exists(excel_path):
        print(f"\n  [!] 엑셀 파일이 없습니다: {excel_path}")
        ans = input("  샘플 파일을 생성할까요? (y/N): ").strip().lower()
        if ans == "y":
            create_sample_excel(excel_path)
        else:
            print("  테스트 데이터 파일을 준비한 뒤 다시 실행하세요.")
            sys.exit(1)

    # ── URL / 브라우저 / 시트 입력 ────────────────────────────────────────────
    url     = args.url     or prompt_url()
    browser = args.browser or prompt_browser()
    sheet   = args.sheet   if args.url else prompt_sheet(excel_path)

    # ── 테스트 실행 ───────────────────────────────────────────────────────────
    if args.run_suite:
        run_suite(
            url=url,
            browser=browser,
            sheet_name="test_suite",
            excel_path=excel_path if args.file else None,
            suite_name=args.suite or "E2E Full Suite",
        )
    else:
        run_tests(
            url=url,
            browser=browser,
            sheet_name=sheet,
            excel_path=excel_path if args.file else None,
            suite_name=args.suite,
        )


if __name__ == "__main__":
    main()

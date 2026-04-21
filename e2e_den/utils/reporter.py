"""
Reporter - 테스트 결과를 수집하고 HTML/콘솔 리포트로 출력하는 유틸리티
"""

import os
import json
import time
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import PATHS

logger = logging.getLogger(__name__)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_SKIP = "SKIP"
STATUS_ERROR = "ERROR"


@dataclass
class TestResult:
    test_id:     str
    description: str
    status:      str
    duration:    float = 0.0
    error_msg:   Optional[str] = None
    screenshot:  Optional[str] = None
    url:         Optional[str] = None
    browser:     Optional[str] = None
    timestamp:   str = field(default_factory=lambda: datetime.now().isoformat())


class Reporter:
    def __init__(self, suite_name: str = "E2E Test Suite"):
        self.suite_name = suite_name
        self.results: List[TestResult] = []
        self.start_time = time.time()

    def add(self, result: TestResult) -> None:
        self.results.append(result)
        icon = {"PASS": "✓", "FAIL": "✗", "SKIP": "○", "ERROR": "!"}.get(result.status, "?")
        print(f"  [{icon}] {result.test_id} | {result.status} | {result.duration:.2f}s | {result.description}")
        if result.error_msg:
            print(f"      └─ {result.error_msg}")

    def summary(self) -> dict:
        total    = len(self.results)
        passed   = sum(1 for r in self.results if r.status == STATUS_PASS)
        failed   = sum(1 for r in self.results if r.status == STATUS_FAIL)
        skipped  = sum(1 for r in self.results if r.status == STATUS_SKIP)
        errors   = sum(1 for r in self.results if r.status == STATUS_ERROR)
        duration = round(time.time() - self.start_time, 2)
        return {
            "suite":    self.suite_name,
            "total":    total,
            "passed":   passed,
            "failed":   failed,
            "skipped":  skipped,
            "errors":   errors,
            "duration": duration,
            "pass_rate": f"{(passed / total * 100):.1f}%" if total else "0%",
        }

    def print_summary(self) -> None:
        s = self.summary()
        sep = "─" * 55
        print(f"\n{sep}")
        print(f"  {s['suite']}")
        print(sep)
        print(f"  Total   : {s['total']}")
        print(f"  PASS    : {s['passed']}  ({s['pass_rate']})")
        print(f"  FAIL    : {s['failed']}")
        print(f"  ERROR   : {s['errors']}")
        print(f"  SKIP    : {s['skipped']}")
        print(f"  Duration: {s['duration']}s")
        print(sep)

    def save_json(self, filename: str = None) -> str:
        os.makedirs(PATHS["reports"], exist_ok=True)
        fname = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(PATHS["reports"], fname)
        payload = {"summary": self.summary(), "results": [asdict(r) for r in self.results]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON report saved → {path}")
        return path

    def save_html(self, filename: str = None) -> str:
        os.makedirs(PATHS["reports"], exist_ok=True)
        fname = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path = os.path.join(PATHS["reports"], fname)
        s = self.summary()

        rows = ""
        for r in self.results:
            color = {"PASS": "#2ecc71", "FAIL": "#e74c3c", "SKIP": "#95a5a6", "ERROR": "#e67e22"}.get(r.status, "#bdc3c7")
            shot = f'<a href="{r.screenshot}" target="_blank">📷</a>' if r.screenshot else "-"
            err  = r.error_msg or "-"
            rows += (
                f'<tr>'
                f'<td>{r.test_id}</td>'
                f'<td>{r.description}</td>'
                f'<td style="color:{color};font-weight:bold">{r.status}</td>'
                f'<td>{r.duration:.2f}s</td>'
                f'<td>{r.browser or "-"}</td>'
                f'<td>{r.url or "-"}</td>'
                f'<td style="color:#c0392b;font-size:.85em">{err}</td>'
                f'<td>{shot}</td>'
                f'</tr>\n'
            )

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>{s['suite']} - Report</title>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f4f6f8; }}
    header {{ background: #2c3e50; color: #fff; padding: 20px 30px; }}
    header h1 {{ margin: 0; font-size: 1.5em; }}
    .summary {{ display: flex; gap: 16px; padding: 20px 30px; flex-wrap: wrap; }}
    .card {{ background: #fff; border-radius: 8px; padding: 16px 24px; box-shadow: 0 1px 4px rgba(0,0,0,.1); min-width: 110px; text-align: center; }}
    .card .num {{ font-size: 2em; font-weight: bold; }}
    .card .lbl {{ font-size: .8em; color: #7f8c8d; }}
    .pass {{ color: #2ecc71; }} .fail {{ color: #e74c3c; }} .skip {{ color: #95a5a6; }} .err {{ color: #e67e22; }}
    table {{ width: calc(100% - 60px); margin: 0 30px 30px; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
    th {{ background: #34495e; color: #fff; padding: 10px 12px; text-align: left; font-size: .85em; }}
    td {{ padding: 9px 12px; border-bottom: 1px solid #ecf0f1; font-size: .85em; word-break: break-all; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f9fafb; }}
  </style>
</head>
<body>
  <header><h1>📋 {s['suite']}</h1><p style="margin:4px 0 0;opacity:.7">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Duration: {s['duration']}s</p></header>
  <div class="summary">
    <div class="card"><div class="num">{s['total']}</div><div class="lbl">Total</div></div>
    <div class="card"><div class="num pass">{s['passed']}</div><div class="lbl">Pass ({s['pass_rate']})</div></div>
    <div class="card"><div class="num fail">{s['failed']}</div><div class="lbl">Fail</div></div>
    <div class="card"><div class="num err">{s['errors']}</div><div class="lbl">Error</div></div>
    <div class="card"><div class="num skip">{s['skipped']}</div><div class="lbl">Skip</div></div>
  </div>
  <table>
    <thead><tr><th>Test ID</th><th>Description</th><th>Status</th><th>Duration</th><th>Browser</th><th>URL</th><th>Error</th><th>Shot</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"HTML report saved → {path}")
        return path

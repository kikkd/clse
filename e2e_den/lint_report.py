"""
flake8 결과를 파싱해서 한글+영어 설명이 포함된 HTML 리포트를 생성합니다.
"""
import subprocess
import sys
import os
from datetime import datetime
from collections import defaultdict

# 오류 코드 → (한글 설명, 영어 원문)
CODE_MAP = {
    # E1xx - 들여쓰기
    "E101": ("들여쓰기에 공백과 탭이 혼용됨", "indentation contains mixed spaces and tabs"),
    "E111": ("들여쓰기가 지정된 공백 수의 배수가 아님", "indentation is not a multiple of N spaces"),
    "E114": ("주석 들여쓰기가 올바르지 않음", "indentation is not a multiple of N (comment)"),
    "E117": ("과도한 들여쓰기", "over-indented"),
    # E2xx - 공백
    "E201": ("'(' 뒤에 불필요한 공백", "whitespace after '('"),
    "E202": ("')' 앞에 불필요한 공백", "whitespace before ')'"),
    "E203": ("':' 앞에 불필요한 공백", "whitespace before ':'"),
    "E211": ("'(' 또는 '[' 앞에 불필요한 공백", "whitespace before '(' or '['"),
    "E221": ("연산자 앞에 불필요한 공백", "multiple spaces before operator"),
    "E225": ("연산자 주변에 공백 없음", "missing whitespace around operator"),
    "E231": ("',' 뒤에 공백 없음", "missing whitespace after ','"),
    "E251": ("키워드/파라미터 등호 주변에 불필요한 공백", "unexpected spaces around keyword / parameter equals"),
    "E261": ("인라인 주석 앞에 공백 2개 이상 필요", "at least two spaces before inline comment"),
    "E262": ("인라인 주석은 '# '으로 시작해야 함", "inline comment should start with '# '"),
    "E265": ("블록 주석은 '# '으로 시작해야 함", "block comment should start with '# '"),
    "E266": ("블록 주석의 '#' 개수가 너무 많음", "too many leading '#' for block comment"),
    # E3xx - 빈 줄
    "E301": ("빈 줄이 필요함", "expected N blank lines"),
    "E302": ("함수/클래스 사이에 빈 줄 2개 필요", "expected 2 blank lines"),
    "E303": ("빈 줄이 너무 많음", "too many blank lines"),
    "E304": ("docstring 바로 다음에 빈 줄 불필요", "defs that immediately follow docstrings should not contain a blank line"),
    "E305": ("클래스/함수 정의 후 빈 줄 2개 필요", "expected 2 blank lines after class or function definition"),
    "E306": ("중첩 정의 전 빈 줄 1개 필요", "expected 1 blank line before a nested definition"),
    # E4xx - import
    "E401": ("한 줄에 여러 import 사용", "multiple imports on one line"),
    "E402": ("모듈 import가 파일 최상단에 없음", "module level import not at top of file"),
    # E5xx - 줄 길이
    "E501": ("줄이 너무 김", "line too long"),
    "E502": ("괄호 사이에서 백슬래시 불필요", "the backslash is redundant between brackets"),
    # E7xx - 구문
    "E711": ("None과 비교 시 == 대신 is/is not 사용 권장", "comparison to None"),
    "E712": ("True/False와 비교 시 == 대신 is/is not 사용 권장", "comparison to True or False"),
    "E721": ("type() 비교 대신 isinstance() 사용 권장", "do not compare types, for exact checks use is and is not"),
    "E722": ("bare except 사용 금지", "do not use bare 'except'"),
    "E731": ("lambda 표현식을 변수에 할당하지 말 것", "do not assign a lambda expression, use a def"),
    "E741": ("모호한 변수명 사용 (l, O, I 등)", "ambiguous variable name"),
    "E743": ("모호한 함수명 사용", "ambiguous function name"),
    # E9xx - 런타임
    "E901": ("문법 오류 또는 들여쓰기 오류", "SyntaxError or IndentationError"),
    "E902": ("토큰 오류", "TokenError"),
    # W1xx
    "W191": ("들여쓰기에 탭 사용됨", "indentation contains tabs"),
    # W2xx
    "W291": ("줄 끝에 불필요한 공백", "trailing whitespace"),
    "W292": ("파일 끝에 개행 없음", "no newline at end of file"),
    "W293": ("빈 줄에 공백 포함됨", "whitespace before a blank line"),
    # W3xx
    "W391": ("파일 끝에 빈 줄 있음", "blank line at end of file"),
    # W5xx
    "W503": ("줄 바꿈이 이진 연산자 앞에 위치", "line break before binary operator"),
    "W504": ("줄 바꿈이 이진 연산자 뒤에 위치", "line break after binary operator"),
    # W6xx
    "W605": ("잘못된 이스케이프 시퀀스", "invalid escape sequence"),
    # F4xx - pyflakes import
    "F401": ("import 되었지만 사용되지 않음", "imported but unused"),
    "F402": ("loop 변수에 의해 가려진 import", "import from line N shadowed by loop variable"),
    "F403": ("star import 사용으로 미정의 이름 감지 불가", "'from module import *' used"),
    "F404": ("다른 구문 이후 future import 사용", "future import after other statements"),
    "F405": ("star import로 인해 미정의 이름일 수 있음", "may be undefined or from star imports"),
    # F8xx - pyflakes 이름
    "F811": ("미사용 이름 재정의", "redefinition of unused name from import"),
    "F821": ("미정의 이름 사용", "undefined name"),
    "F841": ("할당되었지만 사용되지 않는 지역 변수", "local variable is assigned to but never used"),
}


CATEGORY_MAP = {
    "E1": ("들여쓰기 오류", "indentation error"),
    "E2": ("공백 오류", "whitespace error"),
    "E3": ("빈 줄 오류", "blank line error"),
    "E4": ("import 오류", "import error"),
    "E5": ("줄 길이 오류", "line length error"),
    "E7": ("구문 오류", "statement error"),
    "E9": ("런타임 오류", "runtime error"),
    "W1": ("들여쓰기 경고", "indentation warning"),
    "W2": ("공백 경고", "whitespace warning"),
    "W3": ("빈 줄 경고", "blank line warning"),
    "W5": ("줄 바꿈 경고", "line break warning"),
    "W6": ("사용 중단 경고", "deprecation warning"),
}


def get_description(code, original_text=""):
    if code[:4] in CODE_MAP:
        ko, en = CODE_MAP[code[:4]]
        return ko, en
    if code[:2] in CATEGORY_MAP:
        ko, en = CATEGORY_MAP[code[:2]]
        return ko, en
    return "기타 오류", original_text or "other error"


def run_flake8():
    result = subprocess.run(
        [sys.executable, "-m", "flake8", ".", "--format=%(path)s::%(row)d::%(col)d::%(code)s::%(text)s"],
        capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout.strip()


def parse_results(output):
    issues = []
    for line in output.splitlines():
        parts = line.split("::")
        if len(parts) == 5:
            path, row, col, code, text = parts
            ko, en = get_description(code, text.strip())
            issues.append({
                "path": path,
                "row": int(row),
                "col": int(col),
                "code": code,
                "text": text.strip(),
                "ko": ko,
                "en": en,
            })
    return issues


def generate_html(issues):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(issues)

    by_file = defaultdict(list)
    for issue in issues:
        by_file[issue["path"]].append(issue)

    by_code = defaultdict(int)
    for issue in issues:
        by_code[issue["code"]] += 1

    status_color = "#22c55e" if total == 0 else "#f97316"
    status_text = "통과" if total == 0 else "오류 발견"

    rows = ""
    for path, file_issues in sorted(by_file.items()):
        rows += f"""
        <tr class="file-row">
            <td colspan="5">
                <span class="file-icon">📄</span>
                <strong>{path}</strong>
                <span class="badge">{len(file_issues)}건</span>
            </td>
        </tr>"""
        for i in issues:
            if i["path"] != path:
                continue
            idx = issues.index(i)
            rows += f"""
        <tr class="issue-row">
            <td class="code-cell">
                <span class="code-badge code-{i['code'][0]}">{i['code']}</span>
            </td>
            <td class="loc-cell">{i['row']}:{i['col']}</td>
            <td class="msg-cell">
                <span class="original-msg">{i['text']}</span>
                <button class="detail-btn" onclick="toggle({idx})">상세 보기 ▾</button>
                <div class="detail-box" id="detail-{idx}">
                    <div class="detail-ko">🇰🇷 {i['ko']}</div>
                    <div class="detail-en">🇺🇸 {i['en']}</div>
                </div>
            </td>
            <td class="file-cell">{path}</td>
            <td></td>
        </tr>"""

    summary_rows = ""
    for code, count in sorted(by_code.items(), key=lambda x: -x[1]):
        ko, en = get_description(code)
        summary_rows += f"""
            <tr>
                <td><span class="code-badge code-{code[0]}">{code}</span></td>
                <td>{count}건</td>
                <td>{ko}</td>
                <td class="en-text">{en}</td>
            </tr>"""

    no_issue_msg = ""
    if total == 0:
        no_issue_msg = '<tr><td colspan="5" class="no-issue">✅ 린트 오류가 없습니다.</td></tr>'

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Lint Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #f8fafc; color: #1e293b; font-size: 14px; }}
  .header {{ background: #1e293b; color: white; padding: 24px 32px; }}
  .header h1 {{ font-size: 20px; font-weight: 700; }}
  .header .meta {{ font-size: 12px; color: #94a3b8; margin-top: 6px; }}
  .status-badge {{ display: inline-block; background: {status_color}; color: white;
                   padding: 4px 14px; border-radius: 20px; font-size: 13px;
                   font-weight: 700; margin-left: 12px; }}
  .container {{ padding: 24px 32px; }}
  .summary-cards {{ display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }}
  .card {{ background: white; border-radius: 10px; padding: 16px 24px;
           box-shadow: 0 1px 4px rgba(0,0,0,0.08); min-width: 140px; text-align: center; }}
  .card .num {{ font-size: 32px; font-weight: 800; color: #1e293b; }}
  .card .label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
  .card.error .num {{ color: #ef4444; }}
  .card.warn .num {{ color: #f97316; }}
  .section-title {{ font-size: 15px; font-weight: 700; color: #1e293b;
                    margin: 24px 0 12px; border-left: 4px solid #3b82f6;
                    padding-left: 10px; }}
  table {{ width: 100%; border-collapse: collapse; background: white;
           border-radius: 10px; overflow: hidden;
           box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 28px; }}
  th {{ background: #f1f5f9; font-size: 12px; font-weight: 700; color: #475569;
        padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  .file-row td {{ background: #f8fafc; color: #334155; font-size: 13px; }}
  .file-icon {{ margin-right: 6px; }}
  .badge {{ background: #e2e8f0; color: #475569; font-size: 11px;
            padding: 2px 8px; border-radius: 10px; margin-left: 8px; }}
  .code-badge {{ display: inline-block; font-size: 11px; font-weight: 700;
                 padding: 2px 8px; border-radius: 4px; }}
  .code-E {{ background: #fee2e2; color: #991b1b; }}
  .code-W {{ background: #fef3c7; color: #92400e; }}
  .loc-cell {{ color: #64748b; font-size: 12px; white-space: nowrap; }}
  .file-cell {{ color: #94a3b8; font-size: 11px; max-width: 200px;
                overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .original-msg {{ color: #475569; font-size: 13px; }}
  .detail-btn {{ background: none; border: 1px solid #cbd5e1; color: #64748b;
                 font-size: 11px; padding: 2px 8px; border-radius: 4px;
                 cursor: pointer; margin-left: 8px; }}
  .detail-btn:hover {{ background: #f1f5f9; }}
  .detail-box {{ display: none; margin-top: 8px; padding: 10px 14px;
                 background: #f8fafc; border-left: 3px solid #3b82f6;
                 border-radius: 4px; font-size: 13px; }}
  .detail-ko {{ color: #1e40af; font-weight: 600; margin-bottom: 4px; }}
  .detail-en {{ color: #64748b; }}
  .en-text {{ color: #94a3b8; font-size: 12px; }}
  .no-issue {{ text-align: center; padding: 32px; color: #22c55e;
               font-weight: 700; font-size: 15px; }}
  .msg-cell {{ min-width: 300px; }}
  .code-cell {{ white-space: nowrap; }}
</style>
</head>
<body>

<div class="header">
  <h1>🔍 Lint Report <span class="status-badge">{status_text}</span></h1>
  <div class="meta">생성 시각: {now} &nbsp;|&nbsp; 총 오류: {total}건</div>
</div>

<div class="container">

  <div class="summary-cards">
    <div class="card {'error' if total > 0 else ''}">
      <div class="num">{total}</div>
      <div class="label">전체 오류</div>
    </div>
    <div class="card warn">
      <div class="num">{sum(1 for i in issues if i['code'].startswith('E'))}</div>
      <div class="label">Error (E)</div>
    </div>
    <div class="card">
      <div class="num">{sum(1 for i in issues if i['code'].startswith('W'))}</div>
      <div class="label">Warning (W)</div>
    </div>
    <div class="card">
      <div class="num">{len(by_file)}</div>
      <div class="label">영향받는 파일</div>
    </div>
  </div>

  <div class="section-title">오류 유형별 요약</div>
  <table>
    <thead>
      <tr>
        <th>코드</th><th>건수</th><th>한글 설명</th><th>영어 원문</th>
      </tr>
    </thead>
    <tbody>
      {summary_rows if summary_rows else '<tr><td colspan="4" class="no-issue">✅ 오류 없음</td></tr>'}
    </tbody>
  </table>

  <div class="section-title">파일별 오류 목록</div>
  <table>
    <thead>
      <tr>
        <th>코드</th><th>위치</th><th>메시지</th><th>파일</th><th></th>
      </tr>
    </thead>
    <tbody>
      {rows if rows else no_issue_msg}
    </tbody>
  </table>

</div>

<script>
function toggle(idx) {{
  const box = document.getElementById('detail-' + idx);
  const btn = box.previousElementSibling;
  if (box.style.display === 'block') {{
    box.style.display = 'none';
    btn.textContent = '상세 보기 ▾';
  }} else {{
    box.style.display = 'block';
    btn.textContent = '닫기 ▴';
  }}
}}
</script>

</body>
</html>"""
    return html


if __name__ == "__main__":
    os.makedirs("reports/lint", exist_ok=True)
    output = run_flake8()
    issues = parse_results(output)
    html = generate_html(issues)
    with open("reports/lint/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Lint 완료 - 총 {len(issues)}건 | reports/lint/index.html 생성됨")

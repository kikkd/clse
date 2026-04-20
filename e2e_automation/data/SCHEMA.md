# test_data.xlsx 시트 스키마

## 공통 필수 컬럼 (모든 시트)
| 컬럼 | 설명 |
|------|------|
| test_id | 테스트 케이스 ID (예: TC_LOGIN_001) |
| test_type | 실행할 테스트 종류 (아래 참고) |
| description | 테스트 설명 |

## test_type 종류
| test_type | 설명 | 필요 추가 컬럼 |
|-----------|------|----------------|
| page_load | URL 접속 및 타이틀 확인 | - |
| click | 엘리먼트 클릭 | locator_type, locator_value, (nth), (expected_url_contains) |
| click_and_verify | 클릭 후 다른 엘리먼트 확인 | locator_type, locator_value, verify_locator_type, verify_locator_value, verify_expect |
| input | **텍스트 입력만** (제출 없음) | locator_type, locator_value, input_text, (nth) |
| input_and_submit | 텍스트 입력 후 버튼 클릭까지 한 행에 처리 | input_locator_type, input_locator_value, input_text, submit_locator_type, submit_locator_value |
| verify_text | 엘리먼트 텍스트 확인 | locator_type, locator_value, expected_text |
| verify_present | 엘리먼트 존재 확인 | locator_type, locator_value |
| verify_url | 현재 URL 확인 | expected_url_contains |
| select | 드롭다운 선택 | locator_type, locator_value, select_by, select_value |

## locator_type 값
id / name / xpath / css / class / tag / link_text / partial_link_text

## skip_navigate 컬럼
| 값 | 동작 |
|----|------|
| (비워둠) | 해당 행 실행 전 URL로 navigate (기본 동작) |
| yes / 1 / true / y | navigate 생략 → **이전 행의 페이지 상태 유지** |

### 연속 입력 패턴 (로그인 예시)
```
TC_001  page_load  로그인 페이지 접속        skip_navigate=(빈값)
TC_002  input      아이디 입력    id=username  input_text=admin      skip_navigate=yes
TC_003  input      패스워드 입력  id=password  input_text=admin123   skip_navigate=yes
TC_004  click      로그인 클릭    id=login-btn                       skip_navigate=yes
```
TC_002~004는 `skip_navigate=yes`로 설정해 TC_001에서 열린 페이지를 그대로 유지한다.

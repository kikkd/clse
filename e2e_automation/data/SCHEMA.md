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
| click | 엘리먼트 클릭 | locator_type, locator_value, expected_url_contains |
| input_and_submit | 입력 후 제출 | input_locator_type, input_locator_value, input_text, submit_locator_type, submit_locator_value, expected_result |

## locator_type 값
id / name / xpath / css / class / tag / link_text / partial_link_text

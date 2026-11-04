# CLAUDE.md — 전기차 블로그 자동화 (상시 지침)

모든 설명·주석·로그·결과 보고는 **한글**로 작성한다.

## 목적
국내 전기차 차종별 통합 가이드 글을 매일 1편 만드는 반자동 파이프라인. 네이버 블로그(애드포스트 목표).
핵심은 **틀린 숫자가 발행되지 않는 구조**. 현재 범위는 시스템 뼈대 구축이며 문체·목차 확정은 이후 작업.

## 핵심 원칙
1. 고정 흐름은 파이썬 코드, 판단이 필요한 단계(수집·작성·검증)만 에이전트.
2. 작성자(writer)와 검증자(verifier) 분리. verifier는 draft + 팩트 시트 + 출처만 본다.
3. 팩트 시트에 없는 숫자는 글에 쓰지 않는다. 모든 사실에 출처 URL.
4. 공식 출처(제조사·정부·지자체·한국환경공단) 우선, 언론·커뮤니티는 교차 확인용.
5. 정말 확인 불가한 항목만 `[확인 필요: 항목명 | 사유]`로 표기하고 사람에게 알린다. 추측 금지.
6. 반자동: 발행 직전 완성본까지 자동, 발행은 사람.
7. API 키·계정 정보는 저장소에 올리지 않는다(`.env` + `.gitignore`).

## 환경
- Windows 호환(경로·인코딩 UTF-8), Python 3.11+, 가상환경. 로컬 AI 모델 사용 금지(RAM 8GB).
- 에이전트 호출은 `agents.py` 한 모듈로 분리: A) `claude -p` 헤드리스(기본) / B) Anthropic API.

## 데이터
- 큐 `data/queue.csv` 열: order, brand, model, slug, status, updated_at, note
- 상태: `queued → researching → drafting → verifying → needs_human | ready → published → stale` (+ `hold`)
- 팩트 시트 `facts/<slug>.json` 항목: id, category, label, value, unit, source_url, source_type(official|government|press|community), as_of, retrieved_at, status(verified|conflict|unknown)
- official/government 출처가 없으면 `verified` 불가. 출처 간 불일치는 `conflict`, 미발견은 `unknown`.

## 파이프라인
큐 선택(코드) → researcher → writer → verifier → 린트(코드) → 알림(코드) → 발행 준비(코드) → 발행(사람)

## 알림·발행·갱신
- 확인 필요 1개 이상이면 콘솔 출력 + `output/<slug>/needs_human.md`, 상태 `needs_human`. 이메일/텔레그램은 자리만.
- 자동 발행 금지. 완성본에 제목·본문·태그(차종명 필수)·카테고리(브랜드 > 차종, 공통 정보) 포함.
- 옛 글은 수정하지 않음. 새 시점 글을 쓰고 `output/<slug>/stale_links.md` 생성까지만.

## 하지 말 것
- 문체·목차 임의 확정, 출처 없는 숫자, 자동 발행/로그인 자동화, 키·개인정보 커밋, 로컬 AI 모델 전제.

## 구축 순서 (단계마다 사용자 확인)
1 저장소 초기화 → 2 큐·상태 전환·테스트 → 3 에이전트 3종 → 4 agents.py·pipeline → 5 lint/notify/publish_prep → 6 EV3 시험 운행 → 7 outline.yaml·문체 확정
완료 기준: `python -m evblog run --next` 동작, 모든 사실에 출처, report.md 생성, 마커 있으면 needs_human, 마커 0개+린트 통과 시에만 ready.

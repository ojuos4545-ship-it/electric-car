# 전기차 블로그 자동화 시스템 (ev-blog)

국내 전기차를 차종별로 정리하는 가이드 글을 반자동으로 만드는 파이프라인입니다.
핵심 목표: **틀린 숫자가 발행되지 않게 하는 구조**. 최종 발행은 사람이 합니다.

> 현재 상태: 2단계(큐·상태 전환·테스트) 완료. 이후 단계는 구축 진행에 따라 이 문서를 갱신합니다.

## 설치 (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
copy .env.example .env   # 이후 .env에 필요한 값 입력
```

## 사용법 (구축 완료 후)

```powershell
python -m evblog run --next   # 큐의 다음 차종 처리 시작
```

## 폴더 구조

| 경로 | 설명 |
|---|---|
| `data/queue.csv` | 차종 큐(상태 관리) |
| `data/common/` | 공통 정보(보조금, 충전 요금, 용어) |
| `templates/outline.yaml` | 글 목차 템플릿(자리표시자) |
| `facts/` | 차종별 팩트 시트(JSON, 출처 URL 필수) |
| `output/<slug>/` | draft / verified / report 등 결과물 |
| `.claude/agents/` | researcher / writer / verifier 정의 |
| `src/evblog/` | 파이프라인 코드 |

## 주의

- API 키·계정 정보는 `.env`에만 두고 저장소에 올리지 않습니다.
- 자동 발행·로그인 자동화는 만들지 않습니다.

## 테스트

```powershell
pip install -e .[dev]
pytest
```

## 발행 방침

네이버 블로그 글쓰기 API는 사용할 수 없으므로(사용자 확인), 발행은 항상 사람이 완성본을 붙여넣어 직접 합니다.

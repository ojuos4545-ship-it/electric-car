# 전기차 블로그 글 작성 프로젝트

네이버 블로그에 올릴 전기차 차종별 글을 쓰는 저장소다. 사용자가 `/post <차종>`처럼 **차종만 말해도** 아래 규칙대로 글·이미지·복사용 페이지까지 만든다. 규칙의 원본은 가이드 파일이고, 이 문서에 규칙을 복사해 두지 않는다.

## 글 작성 요청을 받으면 (필수)

아래 4개를 **끝까지 읽고** 나서 쓴다. 충돌하면 1번이 가장 우선한다.

1. `docs/guides/ev-post-rules.md`: 전기차 글 전용 규칙 (제목은 모델명만, 축약, 소제목마다 요약 이미지로 시작, 표 가운데 정렬, 고정 목차)
2. `docs/guides/style-guide.md`: 말투, 서식, 줄 나누기, 붙여넣기 서식
3. `docs/guides/seo-guide.md`: 키워드, 구조, 이미지 마커, 태그
4. `docs/guides/image-guide.md`: 마커를 이미지 파일로 만드는 방법

## 작업 순서

`.claude/commands/post.md`의 순서를 따른다. 도구는 `tools/`에 있다.

* 글: `docs/drafts/<슬러그>.md`, 이미지: `docs/drafts/images/<슬러그>/`, 복사용 페이지: `docs/drafts/<슬러그>.copy.html`
* 이미지: `bash tools/setup_images.sh` → `python3 tools/make_blog_images.py docs/drafts/images/<슬러그>/src docs/drafts/images/<슬러그> --theme=dark` → PNG를 직접 열어 확인
* 복사용 페이지: `python3 tools/make_copy_page.py docs/drafts/<슬러그>.md` (`WARN`이 없을 때까지)
* 세션에 작업 브랜치가 지정되어 있으면 그 브랜치에 커밋·푸시한다. 사용자가 요청하지 않으면 다른 브랜치에는 올리지 않는다.

## 사실 규칙

* 숫자는 출처를 확인한 값만 쓴다. 확인하지 못한 값은 지어내지 않고 "확인하지 못함"과 확인할 곳을 적는다.
* 실제로 열어 읽지 못한 자료는 메타 주석에 그렇게 적고, 보고할 때 사용자에게 알린다.
* API 키·계정 정보는 저장소에 올리지 않는다.

## 출력 언어

모든 설명·주석·보고는 한글로, 결론 먼저 짧게 쓴다. 원고를 채팅에 코드 블록으로 붙여 주지 않는다.

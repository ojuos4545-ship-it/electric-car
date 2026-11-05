# 다크 이미지 표본 (원본 HTML)

`docs/guides/image-guide.md` 8-1절의 다크 + 3D 테마로 만든 완성 예시다. 새 이미지를 만들 때 종류에 맞는 파일을 틀로 쓴다. 구조와 클래스(`.head`, `.row`, `.key`, `.prompt`, `.next` 등)는 그대로 두고 **글자만** 바꾼다. 예시의 문구와 내용은 베끼지 않는다.

| 파일 | 마커 종류 | 용도 |
| :--- | :--- | :--- |
| `01_thumbnail_mcp.html` | 썸네일 | 1080×1080. 라벨, 큰 제목, 부제, 번호 목록 3개, 오른쪽 3D 그림(인라인 SVG) |
| `02_diagram_mcp-flow.html` | 다이어그램 | 노드와 화살표 흐름 |
| `03_card_add-commands.html` | 포인트카드 | 번호 행 3개 + `EXAMPLE` 박스 |
| `04_card_mcp-login.html` | 포인트카드 | 번호 행 3개 + `PROMPT` 박스 |
| `05_table_scope.html` | 비교표 | 표 + `KEY POINT` 박스 |
| `06_card_summary.html` | 포인트카드 | 글 마지막 요약 + `NEXT` 다음 글 예고 |

캡처는 다음 명령으로 한다. HTML은 `src/`에, PNG는 그 위 폴더에 둔다.

```bash
python3 tools/make_blog_images.py docs/drafts/images/<슬러그>/src docs/drafts/images/<슬러그> --theme=dark
```

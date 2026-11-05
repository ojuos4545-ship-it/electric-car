#!/usr/bin/env python3
"""글 마크다운을 네이버 에디터에 붙여 넣을 복사용 HTML 페이지로 바꾼다.

사용법: make_copy_page.py <글.md> [출력.html]
규칙은 docs/guides/style-guide.md 4-3(줄 나누기)과 9장(붙여넣기 서식)을 따른다.
줄 폭이 40자를 넘거나 마지막 줄이 8자 미만이거나, 이미지 폴더(images/<글 이름>/)가 있는데 사진 번호에 맞는 파일이 없으면
WARN을 내고 종료 코드 1로 끝난다.
"""
import html
import re
import sys
from pathlib import Path

LIMIT = 40  # 한 줄 폭 환산 상한
TAIL = 8  # 문장 마지막 줄 최소 폭


def width(s: str) -> float:
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s).replace("**", "").replace("`", "")
    return sum(0.3 if c == " " else 0.56 if ord(c) < 128 else 1 for c in s)


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def inline(s: str) -> str:
    out = []
    for part in re.split(r"(`[^`]+`)", s):
        if len(part) > 1 and part[0] == part[-1] == "`":
            out.append(f'<code style="font-family:monospace">{esc(part[1:-1])}</code>')
            continue
        part = esc(part)
        part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", part)
        part = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', part)
        out.append(part)
    return "".join(out)


def check_lines(lines):
    """줄 폭과 꼬리줄을 검사해 경고 목록을 돌려준다."""
    warns, incode = [], False
    for no, line in lines:
        s = line.strip()
        if s.startswith("```"):
            incode = not incode
            continue
        if incode or not s or s.startswith(("#", "|", "---", "[IMAGE", "<!--")):
            continue
        body = re.sub(r"^(>\s*|[*-]\s+|\d+\.\s+)", "", s)
        w = width(body)
        if w > LIMIT:
            warns.append(f"{no}행 줄이 깁니다 ({w:.1f}자): {s[:30]}")
        if re.search(r"[.?!)]$", body) and w < TAIL and not re.match(r"^([*-]|\d+\.)\s", s):
            warns.append(f"{no}행 꼬리줄입니다 ({w:.1f}자): {s}")
    return warns


def convert(md: str):
    meta_at = md.find("<!-- 아래는")
    body, meta = (md, "") if meta_at < 0 else (md[:meta_at], md[meta_at:])
    tags = " ".join(re.findall(r"#[^\s`]+", re.search(r"\*\*태그:\*\*(.*)", meta).group(1))) if re.search(r"\*\*태그:\*\*", meta) else ""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    lines = body.split("\n")
    title, blocks, photos, para = "", [], [], []
    P = '<p style="word-break:keep-all;overflow-wrap:anywhere;margin:0 0 1.2em">'

    def flush():
        if para:
            blocks.append(P + "<br>\n".join(inline(x) for x in para) + "</p>")
            para.clear()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if s.startswith("```"):
            flush()
            j, code = i + 1, []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j += 1
            blocks.append('<pre style="font-family:monospace;border:1px solid #888;padding:12px;white-space:pre-wrap;word-break:break-all;margin:0 0 1.2em">'
                          + esc("\n".join(code)) + "</pre>")
            i = j + 1
            continue
        if not s:
            flush()
        elif s == "---":
            flush()
            blocks.append("<hr>")
        elif re.match(r"^# ", s) and not title:
            flush()
            title = s[2:].strip()
        elif re.match(r"^#{2,3} ", s):
            flush()
            lvl = len(s) - len(s.lstrip("#"))
            size = "1.5em" if lvl == 2 else "1.2em"
            blocks.append(f'<h{lvl} style="font-size:{size};margin:1.6em 0 .6em">{inline(s[lvl + 1:])}</h{lvl}>')
        elif s.startswith("[IMAGE:"):
            flush()
            m = re.match(r"\[IMAGE:\s*([^|\]]+?)\s*\|\s*설명:\s*(.*)\]$", s)
            kind, desc = (m.group(1), m.group(2)) if m else ("", s)
            photos.append((kind, desc))
            blocks.append('<div style="background:#FFE45C;color:#000;text-align:center;padding:18px;margin:0 0 1.2em;font-weight:bold">'
                          f"【사진 {len(photos):02d}】</div>")
        elif s.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            blocks.append('<blockquote style="margin:0 0 1.2em;padding:8px 16px;border-left:4px solid #888;word-break:keep-all">'
                          + "<br>\n".join(inline(x) for x in quote) + "</blockquote>")
            continue
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            cell = "border:1px solid #888;padding:8px;text-align:center;vertical-align:middle;word-break:keep-all"
            head = "".join(f'<th style="{cell};background:#3A3852;color:#FFFFFF">{inline(c)}</th>' for c in rows[0])
            rest = [r for r in rows[2:]]
            trs = "".join("<tr>" + "".join(f'<td style="{cell}">{inline(c)}</td>' for c in r) + "</tr>" for r in rest)
            blocks.append(f'<table style="border-collapse:collapse;width:100%;margin:0 0 1.2em"><tr>{head}</tr>{trs}</table>')
            continue
        elif re.match(r"^([*-]|\d+\.)\s", s):
            flush()
            items = []
            while i < len(lines) and re.match(r"^([*-]|\d+\.)\s", lines[i].strip()):
                m = re.match(r"^([*-]|\d+\.)\s+(.*)", lines[i].strip())
                items.append(("• " if m.group(1) in "*-" else m.group(1) + " ") + m.group(2))
                i += 1
            # 목록 태그는 에디터에서 모양이 틀어질 수 있어 문자 머리표로 쓴다
            blocks.append(P + "<br>\n".join(inline(x) for x in items) + "</p>")
            continue
        else:
            para.append(line)
        i += 1
    flush()
    return title, tags, photos, "\n".join(blocks), check_lines([(n + 1, l) for n, l in enumerate(md.split("\n")[: body_line_count(md, meta_at)])])


def body_line_count(md, meta_at):
    return len(md.split("\n")) if meta_at < 0 else md[:meta_at].count("\n")


PAGE = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>복사용 페이지: {title}</title>
<style>
body{{font-family:-apple-system,"Noto Sans KR","Malgun Gothic",sans-serif;max-width:760px;margin:0 auto;padding:16px;line-height:1.7}}
.panel{{border:1px solid #bbb;border-radius:10px;padding:14px 16px;margin:0 0 18px;font-size:14px}}
.panel h2{{font-size:15px;margin:0 0 8px}}
.panel table{{border-collapse:collapse;width:100%}}.panel td,.panel th{{border-bottom:1px solid #ddd;padding:5px 6px;text-align:left;font-size:13px}}
button{{font:inherit;padding:6px 12px;border:1px solid #888;border-radius:6px;background:#f4f4f4;cursor:pointer}}
.warn{{color:#b00020}}.ok{{color:#1b7f3b}}
#copy-area{{font-size:15px}}
</style></head><body>
<div class="panel"><h2>1. 제목 (블로그 제목 칸에 붙여넣기)</h2>
<div id="title">{title}</div> <button data-copy="title">제목 복사</button></div>
<div class="panel"><h2>2. 본문 (아래 구분선 사이 내용을 에디터에 붙여넣기)</h2>
<button id="copy-body">본문 전체 선택하고 복사</button> <span id="msg"></span>
<p style="margin:8px 0 0">붙여넣은 뒤 노란 칸 <b>【사진 NN】</b>을 해당 번호 이미지로 바꿉니다.</p></div>
<div class="panel"><h2>3. 사진 자리</h2>{photo_table}</div>
<div class="panel"><h2>4. 태그 (태그 입력란에 붙여넣기)</h2>
<div id="tags">{tags}</div> <button data-copy="tags">태그 복사</button></div>
<div class="panel"><h2>5. 줄 점검</h2>{warns}</div>
<hr style="border:0;border-top:2px dashed #999;margin:22px 0">
<div id="copy-area">
{body}
</div>
<hr style="border:0;border-top:2px dashed #999;margin:22px 0">
<script>
function done(t){{var m=document.getElementById('msg');m.textContent=t;setTimeout(function(){{m.textContent=''}},2500)}}
document.querySelectorAll('[data-copy]').forEach(function(b){{b.onclick=function(){{
  var t=document.getElementById(b.dataset.copy).textContent;
  (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){{done('복사했습니다')}},function(){{done('복사 실패: 직접 선택해 복사하세요')}});}}}});
document.getElementById('copy-body').onclick=function(){{
  var r=document.createRange();r.selectNodeContents(document.getElementById('copy-area'));
  var s=getSelection();s.removeAllRanges();s.addRange(r);
  done(document.execCommand('copy')?'복사했습니다':'선택했습니다. Ctrl+C로 복사하세요');}};
</script></body></html>
"""


def main(src: Path, out: Path) -> int:
    md = src.read_text(encoding="utf-8")
    title, tags, photos, body, warns = convert(md)
    imgdir = src.parent / "images" / src.stem
    def image_name(n):
        found = sorted(f for f in imgdir.glob(f"{n:02d}_*") if f.suffix in (".png", ".jpg")) if imgdir.is_dir() else []
        return found[0].name if found else None
    if imgdir.is_dir():  # 이미지 폴더가 있으면 마커 개수만큼 파일이 있어야 한다
        warns += [f"사진 {n:02d} 이미지 파일이 없습니다 ({imgdir}/{n:02d}_*)" for n in range(1, len(photos) + 1) if not image_name(n)]
    rows = "".join(
        f"<tr><td>{n:02d}</td><td>{esc(k)}</td><td>{esc(d)}</td><td>{esc(image_name(n) or '(아직 없음)')}</td></tr>"
        for n, (k, d) in enumerate(photos, 1)
    ) or '<tr><td colspan="4">이미지 마커가 없습니다</td></tr>'
    photo_table = f"<table><tr><th>번호</th><th>종류</th><th>설명</th><th>파일 이름</th></tr>{rows}</table>"
    warn_html = ('<span class="ok">문제 없음: 40자 초과 줄, 8자 미만 꼬리줄, 누락된 이미지가 없습니다.</span>' if not warns
                 else "".join(f'<div class="warn">{esc(w)}</div>' for w in warns))
    out.write_text(PAGE.format(title=esc(title), tags=esc(tags), photo_table=photo_table, warns=warn_html, body=body), encoding="utf-8")
    print(f"{'OK  ' if not warns else 'WARN'} {out} (사진 자리 {len(photos)}개, 태그 {len(tags.split())}개)")
    for w in warns:
        print("   -", w)
    return 1 if warns else 0


if __name__ == "__main__":
    if not 2 <= len(sys.argv) <= 3:
        sys.exit("사용법: make_copy_page.py <글.md> [출력.html]")
    src = Path(sys.argv[1])
    sys.exit(main(src, Path(sys.argv[2]) if len(sys.argv) == 3 else src.with_suffix(".copy.html")))

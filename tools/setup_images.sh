#!/usr/bin/env bash
# 이미지 제작 환경을 준비한다. 여러 번 실행해도 안전하다.
# 파이썬 playwright 패키지와 한글 폰트(Noto Sans CJK KR)가 없으면 설치한다.
set -e
python3 -c "import playwright" 2>/dev/null || pip install -q playwright
if ! fc-list | grep -qi "Noto Sans CJK KR"; then
  apt-get update -q >/dev/null
  apt-get install -y -q fonts-noto-cjk >/dev/null
fi
echo "OK: playwright, 한글 폰트 준비 완료"

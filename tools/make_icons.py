"""
데이터 분석 용어 랩 앱 아이콘 만들기 도구

청록 바탕에 흰 막대그래프 3개, 노란 추세선, 아래 '용어' 글자가 들어간 아이콘을 docs/icons/ 에 만든다.

사용법 (저장소 맨 위 폴더에서, 윈도우 PC):
    pip install pillow
    python tools/make_icons.py
아이콘을 바꾼 뒤에는 docs/sw.js 의 VERSION 도 올려야 폰에 반영된다.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'icons')
BOLD = 'C:/Windows/Fonts/malgunbd.ttf'
TEAL, WHITE, SUN = '#0f5e5a', '#ffffff', '#f6c343'


def make(size, pad=0.0):
    S = 1024
    im = Image.new('RGB', (S, S), TEAL)
    d = ImageDraw.Draw(im)
    k, o = 1 - pad * 2, S * pad
    P = lambda x, y: (o + x * k, o + y * k)
    # 막대그래프 3개 (아래가 같은 선에서 시작)
    base = 640
    for x, h in [(250, 180), (450, 300), (650, 420)]:
        x0, y0 = P(x, base - h); x1, y1 = P(x + 130, base)
        d.rounded_rectangle([x0, y0, x1, y1], radius=int(24 * k), fill=WHITE)
    # 노란 추세선과 점
    pts = [P(315, 400), P(515, 290), P(715, 170)]
    d.line(pts, fill=SUN, width=int(34 * k), joint='curve')
    for x, y in pts:
        r = 34 * k
        d.ellipse([x - r, y - r, x + r, y + r], fill=SUN)
    d.text(P(512, 820), '용어', font=ImageFont.truetype(BOLD, int(190 * k)), fill=WHITE, anchor='mm')
    return im.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, size, pad in [('icon-192.png', 192, 0), ('icon-512.png', 512, 0),
                            ('apple-touch-icon.png', 180, 0), ('icon-maskable-512.png', 512, 0.1)]:
        make(size, pad).save(os.path.join(OUT, name))
        print('docs/icons/' + name)


if __name__ == '__main__':
    main()

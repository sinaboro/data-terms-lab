"""
교안 PDF 만들기: guide/*.md → 데이터분석_용어_학습교안.pdf (ReportLab)

사용법 (저장소 맨 위 폴더에서):
    pip install reportlab
    python tools/build_pdf.py
예제 코드는 실제로 실행해서 결과를 넣는다 (guide_lib.load_all).
코드 글꼴 D2Coding 은 처음 실행할 때 tools/.cache 에 내려받는다 (SIL OFL).
"""
import os
import re
import sys
import urllib.request
import zipfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guide_lib import ROOT, GUIDE, load_all, check  # noqa: E402

OUT = os.path.join(ROOT, '데이터분석_용어_학습교안.pdf')
CACHE = os.path.join(ROOT, 'tools', '.cache')
D2_URL = 'https://github.com/naver/d2codingfont/releases/download/VER1.3.2/D2Coding-Ver1.3.2-20180524.zip'
TITLE = '데이터 분석 용어 학습 교안'
APP_URL = 'https://sinaboro.github.io/data-terms-lab/'

# ───────── 글꼴 ─────────
def fonts():
    d2 = os.path.join(CACHE, 'D2Coding.ttf')
    if not os.path.exists(d2):
        os.makedirs(CACHE, exist_ok=True)
        print('D2Coding 글꼴 내려받는 중...')
        zp = os.path.join(CACHE, 'd2.zip')
        urllib.request.urlretrieve(D2_URL, zp)
        z = zipfile.ZipFile(zp)
        for n in z.namelist():
            if n.endswith('D2Coding/D2Coding-Ver1.3.2-20180524.ttf'):
                open(d2, 'wb').write(z.read(n))
            if n.endswith('D2Coding/D2CodingBold-Ver1.3.2-20180524.ttf'):
                open(os.path.join(CACHE, 'D2CodingBold.ttf'), 'wb').write(z.read(n))
    pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
    pdfmetrics.registerFont(TTFont('MalgunB', 'C:/Windows/Fonts/malgunbd.ttf'))
    pdfmetrics.registerFont(TTFont('D2', d2))
    pdfmetrics.registerFont(TTFont('D2B', os.path.join(CACHE, 'D2CodingBold.ttf')))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily('Malgun', normal='Malgun', bold='MalgunB', italic='Malgun', boldItalic='MalgunB')
    registerFontFamily('D2', normal='D2', bold='D2B', italic='D2', boldItalic='D2B')


# ───────── 색과 글자 모양 ─────────
NAVY = colors.HexColor('#0f5e5a'); ORANGE = colors.HexColor('#e8740c'); BLUE = colors.HexColor('#13807a')
GRAY = colors.HexColor('#5b6475'); LINE = colors.HexColor('#d5dae4')
CODE_BG = colors.HexColor('#f4f6fa'); OUT_BG = colors.HexColor('#fff8ec')
TIP_BG = colors.HexColor('#e6f4f2'); WARN_BG = colors.HexColor('#fdecea')

def S(name, **kw):
    base = dict(fontName='Malgun', fontSize=10, leading=16, wordWrap='CJK', textColor=colors.HexColor('#1b2033'))
    base.update(kw)
    return ParagraphStyle(name, **base)

ST = {
    'p': S('p', spaceAfter=5),
    'li': S('li', leftIndent=12, bulletIndent=2, spaceAfter=2),
    'h1': S('h1', fontName='MalgunB', fontSize=22, leading=30, textColor=NAVY, spaceAfter=4),
    'h1no': S('h1no', fontName='MalgunB', fontSize=12, leading=16, textColor=ORANGE),
    'h2': S('h2', fontName='MalgunB', fontSize=14.5, leading=21, textColor=NAVY, spaceBefore=12, spaceAfter=6),
    'h3': S('h3', fontName='MalgunB', fontSize=11.5, leading=17, textColor=BLUE, spaceBefore=7, spaceAfter=3),
    'code': S('code', fontName='D2', fontSize=8.4, leading=11.6, textColor=colors.HexColor('#1e2a44')),
    'label': S('label', fontName='MalgunB', fontSize=7.5, leading=10, textColor=GRAY),
    'cell': S('cell', fontSize=8.8, leading=12.5),
    'cellh': S('cellh', fontName='MalgunB', fontSize=8.8, leading=12.5, textColor=NAVY),
    'box': S('box', fontSize=9.5, leading=15),
    'q': S('q', fontName='MalgunB', fontSize=10, leading=15, spaceBefore=6, spaceAfter=2),
    'opt': S('opt', fontSize=9.5, leading=14, leftIndent=12),
    'toc0': S('toc0', fontName='MalgunB', fontSize=11, leading=19),
    'toc1': S('toc1', fontSize=9.5, leading=15, leftIndent=14, textColor=GRAY),
    'toc2': S('toc2', fontSize=8.8, leading=13.5, leftIndent=30, textColor=GRAY),
    'h2s': S('h2s', fontName='MalgunB', fontSize=12.5, leading=18, textColor=NAVY, spaceBefore=10, spaceAfter=5),
}

# ───────── 글 다듬기 ─────────
EMOJI = re.compile('[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F]')
def clean(t):
    t = EMOJI.sub('', t).replace('\u2212', '-').replace('≈', '≒')
    return t.strip()

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline(t):
    """**굵게**, `코드` 를 ReportLab 표시로 바꾼다."""
    t = esc(clean(t))
    codes = []                                   # `코드` 안의 ** 가 굵게로 바뀌지 않도록 먼저 빼 둔다
    t = re.sub(r'`([^`]+)`', lambda m: codes.append(m.group(1)) or f'\x00{len(codes) - 1}\x00', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return re.sub('\x00(\\d+)\x00', lambda m: f'<font face="D2" color="#b4441b">{codes[int(m.group(1))]}</font>', t)

def code_para(line, style):
    s = esc(line.replace('\t', '    ')).replace(' ', '&nbsp;')
    return Paragraph(s or '&nbsp;', style)


# ───────── 블록 → 흐름 요소 ─────────
W = A4[0] - 36 * mm

def box_lines(lines, bg, label, border):
    """코드·결과 상자. 줄마다 행을 나눠 페이지 넘김이 자연스럽게 되게 한다."""
    rows = [[Paragraph(label, ST['label'])]] + [[code_para(l, ST['code'])] for l in lines]
    t = Table(rows, colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg), ('LINEBEFORE', (0, 0), (0, -1), 2.2, border),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 0.4), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.4),
        ('TOPPADDING', (0, 0), (-1, 0), 4), ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
    ]))
    t.spaceAfter = 6
    # 짧은 상자는 쪼개지지 않게 (제목만 쪽 끝에 남는 것 방지), 긴 상자는 줄 단위로 넘긴다
    return KeepTogether([t]) if len(lines) <= 22 else t

def note(text, bg, title, color):
    p = Paragraph(f'<font face="MalgunB" color="{color}">{title}</font>&nbsp;&nbsp;' + inline(text).replace('\n', '<br/>'), ST['box'])
    t = Table([[p]], colWidths=[W])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('LEFTPADDING', (0, 0), (-1, -1), 9),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, -1), 6),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    t.spaceAfter = 7
    return t

def table(rows):
    n = max(len(r) for r in rows)
    rows = [r + [''] * (n - len(r)) for r in rows]
    lens = [max(len(clean(r[c])) for r in rows) + 2 for c in range(n)]
    tot = sum(lens)
    widths = [max(W * 0.1, W * l / tot) for l in lens]
    k = W / sum(widths); widths = [w * k for w in widths]
    data = [[Paragraph(inline(c), ST['cellh'] if i == 0 else ST['cell']) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2f0')), ('GRID', (0, 0), (-1, -1), 0.5, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    t.spaceAfter = 8
    return t

def figure(src, alt):
    """그림: 폭을 본문의 82% 이하로 맞추고 아래에 설명을 붙인다."""
    path = os.path.join(GUIDE, src)
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize()
    w = min(W * 0.82, iw * 0.55)
    h = w * ih / iw
    if h > 95 * mm:                      # 너무 길면 높이 기준으로 줄인다
        h = 95 * mm; w = h * iw / ih
    cap = Paragraph(f'▲ {inline(alt)}', S('cap', fontSize=8.5, leading=12, textColor=GRAY, alignment=TA_CENTER))
    return KeepTogether([Spacer(1, 3), Image(path, width=w, height=h), Spacer(1, 2), cap, Spacer(1, 8)])


def term_box(term):
    """절 제목 바로 아래: 영어 이름 + 한 줄 뜻"""
    p = Paragraph(f'<font face="MalgunB" color="#13807a">{esc(clean(term["en"]))}</font><br/>'
                  f'<font face="MalgunB">{inline(term["mean"])}</font>', S('tb', fontSize=10.5, leading=16))
    t = Table([[p]], colWidths=[W])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f4f2')),
                           ('LINEBEFORE', (0, 0), (0, -1), 3, BLUE),
                           ('LEFTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 5),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    t.spaceAfter = 6
    return t


def blocks(bl):
    out = []
    for b in bl:
        t = b['t']
        if t == 'p':
            out.append(Paragraph(inline(b['text']), ST['p']))
        elif t == 'h3':
            out.append(Paragraph(inline(b['text']), ST['h3']))
        elif t in ('ul', 'ol'):
            for k, it in enumerate(b['items'], 1):
                out.append(Paragraph(inline(it), ST['li'], bulletText=f'{k}.' if t == 'ol' else '•'))
            out.append(Spacer(1, 4))
        elif t == 'tip':
            out.append(note(b['text'], TIP_BG, 'TIP', '#2f6fdb'))
        elif t == 'warn':
            out.append(note(b['text'], WARN_BG, '주의', '#c0392b'))
        elif t == 'table':
            out.append(table(b['rows']))
        elif t == 'img':
            out.append(figure(b['src'], b['alt']))
        elif t == 'code':
            if b['lang'] == 'python':
                label = f'파일: {b["file"]}' if b.get('file') else ('파이썬 코드 (실행하지 않는 예시)' if b.get('norun') else '파이썬 코드')
                out.append(box_lines(b['code'].split('\n'), CODE_BG, label, BLUE))
                if b.get('out') is not None:
                    o = b['out'] or '(출력 없음)'
                    out.append(box_lines(o.split('\n'), OUT_BG, '실행 결과' + (f'  ·  입력값: {", ".join(x or "(Enter)" for x in b["input"])}' if b.get('input') else ''), ORANGE))
            else:
                out.append(box_lines(b['code'].split('\n'), colors.HexColor('#eef0f3'), '화면', GRAY))
    return out

def quiz_block(quiz, title):
    out = [Paragraph(title, ST['h2'])]
    for k, q in enumerate(quiz, 1):
        items = [Paragraph(f'Q{k}. {inline(q["q"])}', ST['q'])]
        items += [Paragraph(f'{"①②③④⑤"[j]} {inline(o)}', ST['opt']) for j, o in enumerate(q['o'])]
        out.append(KeepTogether(items))
    return out


# ───────── 문서 틀 (목차·책갈피·쪽 번호) ─────────
class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=17 * mm,
                         title=TITLE, author='김대철')
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='f')
        self.addPageTemplates([PageTemplate('cover', [frame], onPage=lambda c, d: None),
                               PageTemplate('body', [frame], onPage=self.deco)])

    def deco(self, c, d):
        c.saveState(); c.setFont('Malgun', 8); c.setFillColor(GRAY)
        c.drawString(18 * mm, 10 * mm, TITLE)
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(d.page))
        c.setStrokeColor(LINE); c.line(18 * mm, 13.5 * mm, A4[0] - 18 * mm, 13.5 * mm)
        c.restoreState()

    def afterFlowable(self, f):
        lv = getattr(f, 'toc_level', None)
        if lv is None:
            return
        key = f'k{id(f)}'
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(f.toc_text, key, level=lv, closed=lv == 0)
        self.notify('TOCEntry', (lv, f.toc_text, self.page, key))

def heading(text, style, level, toc_text=None):
    p = Paragraph(inline(text), style)
    p.toc_level, p.toc_text = level, clean(toc_text or text)
    return p


def cover():
    big = S('cv', fontName='MalgunB', fontSize=34, leading=44, textColor=NAVY, alignment=TA_CENTER)
    sub = S('cvs', fontSize=13, leading=20, textColor=GRAY, alignment=TA_CENTER)
    badge = Table([[Paragraph('<font color="white"><b>학습 교안</b></font>', S('b', alignment=TA_CENTER, fontSize=12))]],
                  colWidths=[34 * mm], style=[('BACKGROUND', (0, 0), (-1, -1), ORANGE), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)])
    return [Spacer(1, 55 * mm), badge, Spacer(1, 10 * mm), Paragraph('데이터 분석 용어', big), Paragraph('초보자를 위한 쉬운 풀이', S('c2', fontName='MalgunB', fontSize=18, leading=26, textColor=BLUE, alignment=TA_CENTER)),
            Spacer(1, 8 * mm), Paragraph(f'기초 용어·통계·전처리·EDA·머신러닝·평가·KPI·분석 흐름·pandas 용어까지<br/>{N["ch"]}개 장 · 용어 {N["terms"]}개 · 그림 {N["figs"]}개 · 예제 {N["code"]}개 (실제 실행 결과 포함) · 퀴즈 {N["quiz"]}문제', sub),
            Spacer(1, 60 * mm), Paragraph('강사 김대철', S('a', fontName='MalgunB', fontSize=13, alignment=TA_CENTER)),
            Spacer(1, 3 * mm), Paragraph(f'학습 앱: {APP_URL}', S('u', fontSize=10, textColor=BLUE, alignment=TA_CENTER)), PageBreak()]


def intro_table(rows):
    t = table(rows)
    t._argW[0], t._argW[1] = W * 0.18, W * 0.82
    return t


def intro():
    rows = [['표시', '뜻'], ['용어 상자', '절 제목 아래 초록 상자: 영어 이름과 한 줄 뜻. 먼저 이것만 외워도 좋아요'],
            ['파이썬 코드', '직접 실행해 볼 pandas·scikit-learn 코드 (초록 줄). 같은 장의 코드는 앞에서부터 이어서 실행돼요'],
            ['실행 결과', '그 코드를 실제로 실행한 결과 (주황 줄)'],
            ['TIP', '쉬운 비유, 알아 두면 좋은 내용'], ['주의', '자주 하는 오해·실수'], ['총정리 퀴즈', '장 끝의 확인 문제. 정답과 해설은 맨 뒤에 있어요'],
            ['용어 찾아보기', '맨 뒤 가나다순 용어 목록. 모르는 말이 나오면 여기서 절 번호를 찾으세요']]
    return [heading('이 교안의 사용법', ST['h2'], 0),
            Paragraph('이 교안은 데이터 분석을 처음 공부하는 사람이 <b>용어 때문에 막히지 않도록</b> 만들었어요. 용어마다 <b>한 줄 뜻 → 쉬운 설명과 비유 → 그림 → 실행 예제</b> 순서로 풀었습니다. 예제는 모두 실제로 실행해서 얻은 결과(pandas 3 기준)를 실었어요.', ST['p']),
            intro_table(rows),
            note(f'교안과 똑같은 내용을 담은 학습 앱이 있어요. 스마트폰이나 PC 브라우저에서 {APP_URL} 을 열면 용어를 검색하고, 카드 퀴즈로 외우고, 예제 코드를 고쳐 가며 바로 실행할 수 있어요. 카카오톡으로 링크를 받아 홈 화면에 설치하면 앱처럼 쓸 수 있습니다.', TIP_BG, '학습 앱', '#13807a'),
            Paragraph('공부 순서 추천', ST['h3']),
            Paragraph('① 용어 상자의 한 줄 뜻을 소리 내어 읽고 → ② 설명과 그림으로 <b>왜 그런 이름인지</b> 이해하고 → ③ 예제를 실행해 숫자를 바꿔 보고 → ④ 장 끝 퀴즈와 앱의 카드 퀴즈로 확인하세요. 8장의 전체 흐름 그림을 먼저 보고 시작해도 좋아요.', ST['p']),
            PageBreak()]


def answers(chs):
    out = [heading('정답과 해설', ST['h1'], 0)]          # 앞 장 끝에 이미 PageBreak 가 있다
    for ch in chs:
        if not ch['quiz']:
            continue
        name = f'{ch["no"]}장 총정리 퀴즈'
        out.append(Paragraph(name, ST['h3']))
        rows = [['번호', '정답', '해설']] + [[f'Q{k}', '①②③④⑤'[q['a']], q['e']] for k, q in enumerate(ch['quiz'], 1)]
        t = table(rows)
        t._argW[0], t._argW[1], t._argW[2] = W * 0.08, W * 0.08, W * 0.84
        out.append(t)
    return out


def glossary(chs):
    """맨 뒤 '용어 찾아보기': 가나다순(한글이 없으면 영어) 용어 · 영어 · 한 줄 뜻 · 절 번호"""
    def ko(title):                       # '평균 · Mean' → '평균', 'MAE · 평균 절대 오차' → '평균 절대 오차'
        parts = [x for x in title.split(' · ') if re.search(r'[가-힣]', x)]
        return ' · '.join(parts) if parts else title.split(' · ')[0]
    terms = [(ko(s['title']), s['term'], s['no']) for ch in chs for s in ch['sections'] if s.get('term')]
    key = lambda x: (0 if re.match(r'[가-힣]', x[0]) else 1, x[0].lower())
    rows = [['용어', '영어', '한 줄 뜻', '절']] + [[name, t['en'], t['mean'], no] for name, t, no in sorted(terms, key=key)]
    tb = table(rows)
    tb._argW[0], tb._argW[1], tb._argW[2], tb._argW[3] = W * 0.2, W * 0.24, W * 0.46, W * 0.1
    return [PageBreak(), heading('용어 찾아보기', ST['h1'], 0),
            Paragraph(f'이 교안의 용어 {len(terms)}개를 가나다순으로 모았어요. 오른쪽 <b>절 번호</b>로 찾아가세요. (앱의 \'용어 찾기\' 탭에서는 검색도 돼요)', ST['p']), tb]


N = {}


def main():
    sys.stdout.reconfigure(errors='replace')
    fonts()
    chs = load_all()
    errs = check(chs)
    if errs:
        sys.exit('원고 오류:\n' + '\n'.join(errs))
    N.update(ch=len(chs), terms=sum(1 for c in chs for s in c['sections'] if s.get('term')),
             figs=len({b['src'] for c in chs for s in c['sections'] for b in s['blocks'] if b['t'] == 'img'}),
             code=sum(1 for c in chs for s in c['sections'] for b in s['blocks'] if b['t'] == 'code' and b['lang'] == 'python'),
             quiz=sum(len(c['quiz']) for c in chs))
    story = cover()
    from reportlab.platypus import NextPageTemplate
    story.insert(0, NextPageTemplate('body'))
    story += intro()
    toc = TableOfContents(levelStyles=[ST['toc0'], ST['toc1'], ST['toc2']], dotsMinLevel=0)
    story += [Paragraph('목차', ST['h1']), Spacer(1, 4), toc, PageBreak()]
    for ch in chs:
        is_app = ch['no'] == '부록'
        story.append(Paragraph('APPENDIX' if is_app else f'CHAPTER {ch["no"]}', ST['h1no']))
        story.append(heading(ch['title'], ST['h1'], 0, f'부록  {ch["title"]}' if is_app else f'{ch["no"]}장  {ch["title"]}'))
        if ch['goals']:
            gl = '\n'.join(f'• {g}' for g in ch['goals'])        # note() 가 줄바꿈을 <br/> 로 바꾼다
            story.append(note(gl, colors.HexColor('#fff3e6'), '학습 목표<br/>', '#e8740c'))
        for sec in ch['sections']:
            if sec['title'] != '들어가며':
                label = f'부록 {sec["no"]}. {sec["title"]}' if is_app else f'{sec["no"]} {sec["title"]}'
                sub = sec['no'].count('.') >= 2            # 05.1.3 같은 하위 항목은 목차 한 단계 아래
                h = heading(label, ST['h2s'] if sub else ST['h2'], 2 if sub else 1)
                story.append(KeepTogether([h, term_box(sec['term'])]) if sec.get('term') else h)
            story += blocks(sec['blocks'])
            if is_app and sec['no'] == 'D':
                story += quiz_block(ch['quiz'], '문제')
        if ch['quiz'] and not is_app:
            story += quiz_block(ch['quiz'], '총정리 퀴즈')
        story.append(PageBreak())
    story += answers(chs)
    story += glossary(chs)
    doc = Doc(OUT)
    doc.multiBuild(story)
    print('저장:', OUT, f'({doc.page}쪽)')


if __name__ == '__main__':
    main()

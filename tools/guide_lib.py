"""
교안 원고(guide/chNN.md)를 읽어 구조로 바꾸고, 파이썬 예제를 실제로 실행해 결과를 붙이는 공통 모듈.
build_pdf.py(교안 PDF), build_app.py(앱 데이터), build_code.py(실습코드)가 이 모듈을 함께 쓴다.

원고 문법 (마크다운을 조금 줄인 것)
  # 01 | 장 제목                     장 시작
  @goals ... @end                    학습 목표 (- 로 시작하는 줄)
  ## 01.1 | 절 제목                  절 시작
  ### 소제목                         소제목
  일반 문단, **굵게**, `코드`
  - 목록 / 1. 번호 목록
  > 💡 팁 상자         !> 주의 상자
  | 표 | 머리 |  (둘째 줄 |---|)
  ```python            실행해서 결과를 붙임
  ```python norun      실행하지 않음 (무한 반복, 문법 오류 예시 등)
  ```python input=홍길동|20    input() 에 넣을 값 (| 로 구분)
  ```text              그냥 글 상자 (터미널 화면 등)
  @quiz ... @end       ? 질문 / - 오답 / + 정답 / = 해설
  @term English | 뜻   절 바로 아래: 용어 사전·카드 퀴즈에 쓰는 메타
  ## 05.1.3 | …        3단계 번호 = 하위 항목 (부모 절에 @sub 묶음이름)
  ![설명](figs/a.png)  그림
"""
import builtins
import contextlib
import io
import json
import os
import re
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(ROOT, 'guide')
BUILD = os.path.join(ROOT, 'build')


# ───────── 원고 읽기 ─────────
def parse_file(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    ch = {'no': '', 'title': '', 'goals': [], 'sections': [], 'quiz': []}
    sec = None
    i = 0

    def cur():
        nonlocal sec
        if sec is None:                       # 절 앞에 나오는 글은 '들어가며' 절로
            sec = {'no': ch['no'] + '.0', 'title': '들어가며', 'blocks': []}
            ch['sections'].append(sec)
        return sec['blocks']

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith('# ') and not s.startswith('## '):
            no, title = [x.strip() for x in s[2:].split('|', 1)]
            ch['no'], ch['title'] = no, title
        elif s == '@goals':
            i += 1
            while lines[i].strip() != '@end':
                if lines[i].strip().startswith('- '):
                    ch['goals'].append(lines[i].strip()[2:])
                i += 1
        elif s == '@quiz':
            i += 1
            q = None
            while lines[i].strip() != '@end':
                t = lines[i].strip()
                if t.startswith('? '):
                    q = {'q': t[2:], 'o': [], 'a': -1, 'e': ''}
                    ch['quiz'].append(q)
                elif t.startswith('+ '):
                    q['a'] = len(q['o']); q['o'].append(t[2:])
                elif t.startswith('- '):
                    q['o'].append(t[2:])
                elif t.startswith('= '):
                    q['e'] = t[2:]
                i += 1
        elif s.startswith('## '):
            no, title = [x.strip() for x in s[3:].split('|', 1)]
            sec = {'no': no, 'title': title, 'blocks': []}
            ch['sections'].append(sec)
        elif s.startswith('@sub '):           # 하위 항목 묶음 이름: 앱 장 목차의 하위 메뉴 제목 (예: 대표 모델)
            sec['sub'] = s[5:].strip()
        elif s.startswith('@term '):          # 용어 메타: @term 영어 | 한 줄 뜻 (검색·카드 퀴즈용)
            en, mean = [x.strip() for x in s[6:].split('|', 1)]
            sec['term'] = {'en': en, 'mean': mean}
        elif re.match(r'^!\[.*\]\(.+\)$', s):     # 그림: ![설명](figs/파일.png)
            m = re.match(r'^!\[(.*)\]\((.+)\)$', s)
            cur().append({'t': 'img', 'alt': m.group(1), 'src': m.group(2)})
        elif s.startswith('### '):
            cur().append({'t': 'h3', 'text': s[4:]})
        elif s.startswith('```'):
            info = s[3:].strip()
            lang = info.split()[0] if info else 'text'
            opts = info[len(lang):].strip()
            body = []
            i += 1
            while not lines[i].strip().startswith('```'):
                body.append(lines[i])
                i += 1
            b = {'t': 'code', 'lang': lang, 'code': '\n'.join(body).rstrip('\n')}
            if 'norun' in opts:
                b['norun'] = True
            m = re.search(r'input=(.*?)(?:\s+(?:file=|norun)|$)', opts)   # 입력값에 띄어쓰기가 있어도 됨
            if m:
                b['input'] = m.group(1).split('|')
            m = re.search(r'file=(\S+)', opts)       # 모듈 파일: 실행하지 않고 그 이름의 파일로 저장
            if m:
                b['file'] = m.group(1)
                b['norun'] = True
            cur().append(b)
        elif s.startswith('> ') or s.startswith('!> '):
            kind = 'warn' if s.startswith('!') else 'tip'
            text = s.split('> ', 1)[1]
            while i + 1 < len(lines) and lines[i + 1].strip().startswith('> ') and kind == 'tip':
                i += 1; text += '\n' + lines[i].strip()[2:]
            cur().append({'t': kind, 'text': text})
        elif s.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                r = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in r):
                    rows.append(r)
                i += 1
            i -= 1
            cur().append({'t': 'table', 'rows': rows})
        elif re.match(r'^(- |\d+\. )', s):
            ordered = bool(re.match(r'^\d+\. ', s))
            items = []
            while i < len(lines) and re.match(r'^(- |\d+\. )', lines[i].strip()):
                items.append(re.sub(r'^(- |\d+\. )', '', lines[i].strip()))
                i += 1
            i -= 1
            cur().append({'t': 'ol' if ordered else 'ul', 'items': items})
        elif s:
            text = s
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r'^(#|@|```|> |!> |!\[|\||- |\d+\. )', lines[i + 1].strip()):
                i += 1; text += ' ' + lines[i].strip()
            cur().append({'t': 'p', 'text': text})
        i += 1
    return ch


# ───────── 예제 실행 ─────────
def run_block(code, ns, stdin=None):
    """코드를 실행하고 화면에 나온 글자를 돌려준다. input() 은 미리 준 값으로 대신한다."""
    out = io.StringIO()
    feed = list(stdin or [])

    def fake_input(prompt=''):
        v = feed.pop(0) if feed else ''
        out.write(str(prompt) + v + '\n')   # 터미널처럼 입력한 값도 화면에 보이게
        return v

    old_input = builtins.input
    builtins.input = fake_input
    try:
        with contextlib.redirect_stdout(out):
            try:
                exec(compile(code, '<stdin>', 'exec'), ns)
            except SyntaxError as e:
                out.write(f'  File "<stdin>", line {e.lineno}\n    {(e.text or "").strip()}\n{type(e).__name__}: {e.msg}\n')
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                line = [f for f in tb if f.filename == '<stdin>']
                ln = line[-1].lineno if line else '?'
                src = code.split('\n')[ln - 1].strip() if isinstance(ln, int) else ''
                out.write(f'Traceback (most recent call last):\n  File "<stdin>", line {ln}, in <module>\n    {src}\n'
                          + ''.join(traceback.format_exception_only(type(e), e)))
    finally:
        builtins.input = old_input
    return out.getvalue().rstrip('\n')


def load_all(run=True):
    """guide/ 의 모든 원고를 읽고, 예제를 실행해 결과(out)를 붙여 돌려준다."""
    files = sorted(f for f in os.listdir(GUIDE) if f.endswith('.md'))
    chapters = [parse_file(os.path.join(GUIDE, f)) for f in files]
    if run:
        work = os.path.join(BUILD, 'run')
        os.makedirs(work, exist_ok=True)
        here = os.getcwd()
        os.chdir(work)                         # 파일 읽기·쓰기 예제는 build/run 안에서 실행
        sys.path.insert(0, work)
        try:
            import random
            for ch in chapters:
                ns = {'__name__': '__main__'}     # 장마다 새 실행 공간 (노트북처럼 장 안에서는 이어짐)
                for sec in ch['sections']:
                    for b in sec['blocks']:
                        if b['t'] == 'code' and b.get('file'):
                            open(b['file'], 'w', encoding='utf-8').write(b['code'] + '\n')
                            sys.modules.pop(b['file'][:-3], None)   # 같은 이름 모듈을 새로 읽게
                        if b['t'] == 'code' and b['lang'] == 'python' and not b.get('norun'):
                            random.seed(42)
                            b['out'] = run_block(b['code'], ns, b.get('input'))
        finally:
            os.chdir(here)
    return chapters


def check(chapters):
    """퀴즈 정답 표시 누락 같은 원고 실수를 찾는다."""
    errs = []
    for ch in chapters:
        for k, q in enumerate(ch['quiz']):
            if q['a'] < 0:
                errs.append(f"{ch['no']}장 퀴즈 {k + 1}: 정답(+) 없음")
            if not q['e']:
                errs.append(f"{ch['no']}장 퀴즈 {k + 1}: 해설(=) 없음")
    return errs


if __name__ == '__main__':
    sys.stdout.reconfigure(errors='replace')
    chs = load_all()
    os.makedirs(BUILD, exist_ok=True)
    json.dump(chs, open(os.path.join(BUILD, 'guide.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for ch in chs:
        n_code = sum(1 for s in ch['sections'] for b in s['blocks'] if b['t'] == 'code')
        print(f"{ch['no']} {ch['title']}: 절 {len(ch['sections'])} · 예제 {n_code} · 퀴즈 {len(ch['quiz'])}")
    for e in check(chs):
        print('  [오류]', e)

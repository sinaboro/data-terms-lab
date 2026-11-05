// 데이터 분석 용어 랩 — 화면 이동, 진도 저장, 용어 찾기, 카드 퀴즈, 코드 실행(Pyodide), 앱 설치
// 화면 주소(해시): #/ 홈 · #/c/장 · #/c/장/절 · #/q/장 퀴즈 · #/dict 용어 찾기 · #/cards 카드 퀴즈 · #/help 사용법

const $ = s => document.querySelector(s);
const view = $('#view');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const APP = '데이터 분석 용어 랩';
let tt;
function toast(m, ms = 2200) { const t = $('#toast'); t.textContent = m; t.hidden = false; clearTimeout(tt); tt = setTimeout(() => t.hidden = true, ms); }
const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

// ───────── 진도 저장 ─────────
// 절은 "장/절번호"(예: 03/03.4), 퀴즈는 "q/장", 외운 용어는 "k/절번호" 로 저장 → 내용을 추가해도 기록이 유지된다
const STORE = 'data-terms-progress-v1';
let prog = {};
try { prog = JSON.parse(localStorage.getItem(STORE)) || {}; } catch (e) {}
const saveProg = () => { try { localStorage.setItem(STORE, JSON.stringify(prog)); } catch (e) {} };
const skey = (c, s) => `${c.no}/${s.no}`;
const items = c => c.sections.length + (c.quiz.length ? 1 : 0);
const doneOf = c => c.sections.filter(s => prog[skey(c, s)]).length + (prog['q/' + c.no] ? 1 : 0);
const totalItems = CH.reduce((a, c) => a + items(c), 0);
function nextStep() {
  for (const c of CH) {
    for (const s of c.sections) if (!prog[skey(c, s)]) return { c, s };
    if (c.quiz.length && !prog['q/' + c.no]) return { c, quiz: true };
  }
  return null;
}

// ───────── 용어 목록 (용어 찾기·카드 퀴즈에서 사용) ─────────
const TERMS = CH.flatMap(c => c.sections.filter(s => s.term).map(s => ({
  c, s, id: s.no, name: s.title, en: s.term.en, mean: s.term.mean,
  // 뜻 앞에 붙은 영어 풀이(예: "Mean Absolute Error, …")는 문제에서 정답 힌트가 되므로 뺀다
  hint: s.term.mean.replace(/^[A-Za-z][A-Za-z0-9\s\-²]*,\s*/, ''),
})));
const known = t => !!prog['k/' + t.id];
const setKnown = (t, v) => { if (v) prog['k/' + t.id] = 1; else delete prog['k/' + t.id]; saveProg(); };

// ───────── 화면 이동 ─────────
function route() {
  const p = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean).map(decodeURIComponent);
  const tab = ['dict', 'cards', 'help'].includes(p[0]) ? p[0] : 'home';
  document.querySelectorAll('.tabs a').forEach(a => a.classList.toggle('on', a.dataset.tab === tab));
  const back = $('#back');
  back.hidden = !(p[0] === 'c' || p[0] === 'q');
  if (p[0] === 'c' || p[0] === 'q') {
    const c = CH.find(x => x.no === p[1]);
    if (!c) return go('#/');
    if (p[0] === 'q') { back.onclick = () => go(`#/c/${c.no}`); renderQuiz(c); }
    else if (p[2]) {
      const s = c.sections.find(x => x.no === p[2]);
      if (!s) return go(`#/c/${c.no}`);
      back.onclick = () => history.length > 1 ? history.back() : go(`#/c/${c.no}`); renderSection(c, s);
    } else { back.onclick = () => go('#/'); renderChapter(c); }
  } else if (tab === 'dict') renderDict();
  else if (tab === 'cards') renderCards();
  else if (tab === 'help') renderHelp();
  else renderHome();
  window.scrollTo(0, 0);
}
const go = h => { location.hash = h; };
addEventListener('hashchange', route);

// ───────── 홈 ─────────
function renderHome() {
  $('#title').textContent = APP;
  const done = CH.reduce((a, c) => a + doneOf(c), 0), n = nextStep();
  const nk = TERMS.filter(known).length;
  view.innerHTML = `<div class="stack">
    <div class="hero"><h2>데이터 분석 용어 랩 📊</h2>
      <p>데이터 분석에 꼭 나오는 용어 ${TERMS.length}개를 쉬운 설명·그림·예제로 익혀요.</p>
      <div class="bar"><i style="width:${done / totalItems * 100}%"></i></div>
      <p style="margin-top:6px;font-size:13px">학습 진도 ${done} / ${totalItems} · 외운 용어 ${nk} / ${TERMS.length}</p>
      <button class="cont" id="cont">${n ? `▶ ${done ? '이어서 학습하기' : '첫 장 시작하기'}<br><small style="font-weight:600">${n.c.no}장 · ${n.quiz ? '총정리 퀴즈' : n.s.no + ' ' + esc(n.s.title)}</small>` : '🎉 모두 완료! 처음부터 복습하기'}</button>
    </div>
    <div class="quick"><button data-go="#/dict">🔍 용어 찾기</button><button data-go="#/cards">🃏 카드 퀴즈</button></div>
    ${CH.map(c => `<button class="chap ${doneOf(c) === items(c) ? 'done' : ''}" data-c="${c.no}">
      <span class="no">${doneOf(c) === items(c) ? '✓' : c.no}</span>
      <span class="ct"><b>${c.title}</b><small>용어 ${c.sections.filter(s => s.term).length}개${c.quiz.length ? ` · 퀴즈 ${c.quiz.length}문제` : ''} · 진도 ${doneOf(c)}/${items(c)}</small>
      <span class="bar"><i style="width:${doneOf(c) / items(c) * 100}%"></i></span></span></button>`).join('')}
  </div>`;
  $('#cont').onclick = () => { const x = nextStep(); if (!x) return go(`#/c/${CH[0].no}/${CH[0].sections[0].no}`); go(x.quiz ? `#/q/${x.c.no}` : `#/c/${x.c.no}/${x.s.no}`); };
  view.querySelectorAll('[data-c]').forEach(b => b.onclick = () => go(`#/c/${b.dataset.c}`));
  view.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
}

// ───────── 장 ─────────
// 절 번호가 3단계(05.1.3)면 하위 항목: 장 목차에서 부모 절(05.1) 아래 접었다 펼 수 있는 하위 메뉴로 보여 준다
const isSub = s => s.no.split('.').length > 2;
const parentNo = s => s.no.split('.').slice(0, 2).join('.');
const subsOf = (c, s) => c.sections.filter(x => isSub(x) && parentNo(x) === s.no);
const closedSubs = new Set();                 // 사용자가 접은 하위 메뉴 (기본은 펼침)
const secBtn = (c, s, sub) => `<button class="sec${sub ? ' sub' : ''}" data-s="${s.no}"><span class="k">${s.no}</span><span class="t">${esc(s.title)}${s.term ? `<small>${esc(s.term.mean)}</small>` : ''}</span><span class="ck">${prog[skey(c, s)] ? '✓' : '›'}</span></button>`;
function renderChapter(c) {
  $('#title').textContent = `${c.no}장 ${c.title}`;
  view.innerHTML = `<div class="stack">
    <div class="lhead"><span class="k">CHAPTER ${c.no}</span><h2>${c.title}</h2></div>
    ${c.goals.length ? `<div class="goals"><h3>🎯 학습 목표</h3><ul>${c.goals.map(g => `<li>${g}</li>`).join('')}</ul></div>` : ''}
    ${c.sections.filter(s => !isSub(s)).map(s => {
      const subs = subsOf(c, s);
      if (!subs.length) return secBtn(c, s);
      const open = !closedSubs.has(s.no), done = subs.filter(x => prog[skey(c, x)]).length;
      return secBtn(c, s) + `<div class="subgrp"><button class="subtg" data-tg="${s.no}">${open ? '▾' : '▸'} ${esc(s.title.split(' · ')[0])} ${esc(s.sub || '하위 항목')} ${subs.length}개 <small>(${done}/${subs.length})</small></button>
        <div class="subs" ${open ? '' : 'hidden'}>${subs.map(x => secBtn(c, x, true)).join('')}</div></div>`;
    }).join('')}
    ${c.quiz.length ? `<button class="qbtn" id="qb">📝 총정리 퀴즈 ${c.quiz.length}문제 ${prog['q/' + c.no] ? '· 완료 ✓' : ''}</button>` : ''}
  </div>`;
  view.querySelectorAll('[data-s]').forEach(b => b.onclick = () => go(`#/c/${c.no}/${b.dataset.s}`));
  view.querySelectorAll('[data-tg]').forEach(b => b.onclick = () => {
    const k = b.dataset.tg; closedSubs.has(k) ? closedSubs.delete(k) : closedSubs.add(k);
    const y = scrollY; renderChapter(c); scrollTo(0, y);
  });
  const qb = $('#qb'); if (qb) qb.onclick = () => go(`#/q/${c.no}`);
}

// ───────── 절 (용어 설명 + 그림 + 실행할 수 있는 코드) ─────────
function renderSection(c, s) {
  const i = c.sections.indexOf(s), prev = c.sections[i - 1], next = c.sections[i + 1];
  const ci = CH.indexOf(c), nextCh = CH[ci + 1];
  const t = TERMS.find(x => x.s === s);
  $('#title').textContent = `${s.no} ${s.title}`;
  view.innerHTML = `<div class="stack">
    <div class="lhead"><span class="k">${c.no}장 ${c.title}${isSub(s) ? ` › ${esc(c.sections.find(x => x.no === parentNo(s)).title.split(' · ')[0])}` : ''} · ${i + 1} / ${c.sections.length}</span><h2>${esc(s.title)}</h2></div>
    ${t ? `<div class="termcard"><span class="en">${esc(t.en)}</span><p>${esc(t.mean)}</p>
      <button class="kbtn ${known(t) ? 'on' : ''}" id="kb">${known(t) ? '✓ 외웠어요' : '☆ 외운 용어로 표시'}</button></div>` : ''}
    <div class="card body">${s.html}</div>
    ${subsOf(c, s).length ? `<div class="card"><h3 style="margin:0 0 4px;font-size:16px">📂 ${esc(s.title.split(' · ')[0])} ${esc(s.sub || '하위 항목')} ${subsOf(c, s).length}개</h3>${subsOf(c, s).map(x => secBtn(c, x, true)).join('')}</div>` : ''}
    <div class="nav2">
      ${prev ? `<button data-go="#/c/${c.no}/${prev.no}">‹ 이전</button>` : `<button data-go="#/c/${c.no}">‹ 목차</button>`}
      ${next ? `<button class="pri" data-go="#/c/${c.no}/${next.no}">다음 ›</button>`
        : c.quiz.length ? `<button class="pri" data-go="#/q/${c.no}">📝 총정리 퀴즈 ›</button>`
        : nextCh ? `<button class="pri" data-go="#/c/${nextCh.no}">다음 장 ›</button>` : `<button class="pri" data-go="#/">홈</button>`}
    </div></div>`;
  view.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  view.querySelectorAll('.card [data-s]').forEach(b => b.onclick = () => go(`#/c/${c.no}/${b.dataset.s}`));
  view.querySelectorAll('.cb[data-c]').forEach(el => codeBox(el, CODE[+el.dataset.c]));
  view.querySelectorAll('.body img').forEach(im => im.onclick = () => zoom(im));
  const kb = $('#kb');
  if (kb) kb.onclick = () => { setKnown(t, !known(t)); kb.classList.toggle('on', known(t)); kb.textContent = known(t) ? '✓ 외웠어요' : '☆ 외운 용어로 표시'; };
  if (!prog[skey(c, s)]) { prog[skey(c, s)] = Date.now(); saveProg(); }     // 열어 본 절은 읽음으로 기록
}

// 그림을 누르면 크게 보기
function zoom(im) {
  const z = document.createElement('div'); z.className = 'zoom';
  z.innerHTML = `<img src="${im.src}" alt=""><p>${esc(im.alt)}<br><small>아무 곳이나 누르면 닫혀요</small></p>`;
  z.onclick = () => z.remove(); document.body.appendChild(z);
}

// 코드 상자: 고쳐서 ▶ 실행, ↺ 원래대로, 복사
function codeBox(el, ex) {
  el.innerHTML = `<div class="hd"><span>파이썬${ex.pre.length ? ' · 이어서' : ''}</span><button class="run">▶ 실행</button><button class="rs">↺</button><button class="cp">복사</button></div>
    <textarea spellcheck="false" autocapitalize="off" autocomplete="off"></textarea><div class="out" hidden></div>`;
  const ta = el.querySelector('textarea'), out = el.querySelector('.out');
  const fit = () => { ta.style.height = 'auto'; ta.style.height = ta.scrollHeight + 'px'; };
  ta.value = ex.code; setTimeout(fit, 0);
  ta.addEventListener('input', fit);
  ta.addEventListener('keydown', e => { if (e.key === 'Tab') { e.preventDefault(); document.execCommand('insertText', false, '    '); } });
  const showOut = (text, lb, err, figs = []) => {
    out.hidden = false; out.className = 'out' + (err ? ' err' : '');
    out.innerHTML = `<span class="lb">${lb}</span><pre>${esc(text || (figs.length ? '' : '(출력 없음)'))}</pre>` +
      figs.map(f => `<img class="plot" src="data:image/png;base64,${f}" alt="그래프">`).join('');
  };
  if (ex.out != null) showOut(ex.out, '실행 결과 (교안과 같은 결과)');
  el.querySelector('.run').onclick = async () => {
    const run = el.querySelector('.run');
    run.disabled = true; run.textContent = '⏳';
    try {
      const r = await runPython(ta.value, ex.pre.map(k => CODE[k].code));
      showOut(r.out, r.err ? '오류가 났어요 (마지막 줄을 읽어 보세요)' : '실행 결과', r.err, r.figs);
    } catch (e) { showOut(String(e.message || e), '실행 준비 실패', true); }
    run.disabled = false; run.textContent = '▶ 실행';
  };
  el.querySelector('.rs').onclick = () => { ta.value = ex.code; fit(); toast('원래 코드로 되돌렸어요'); };
  el.querySelector('.cp').onclick = async () => { try { await navigator.clipboard.writeText(ta.value); toast('코드를 복사했어요'); } catch (e) { ta.select(); toast('길게 눌러 복사하세요'); } };
}

// ───────── 파이썬 실행 (Pyodide: 브라우저 안의 파이썬) ─────────
// 처음 실행할 때 파이썬과 pandas 등을 한 번 내려받고, 이후에는 폰에 저장된 것을 써서 인터넷 없이도 실행된다.
const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
let pyReady = null;
function loadPy() {
  if (pyReady) return pyReady;
  pyReady = new Promise((res, rej) => {
    toast('파이썬 준비 중… 처음 한 번은 10~20초 걸려요', 6000);
    const s = document.createElement('script'); s.src = PYODIDE + 'pyodide.js';
    s.onload = async () => {
      try {
        const py = await loadPyodide({ indexURL: PYODIDE });
        // _run: 앞 예제를 조용히 먼저 실행 → 내 코드 실행 → 화면 출력과 그래프(PNG)를 JSON 으로 돌려줌
        py.runPython(`
import sys, io, os, json, base64, traceback, warnings, contextlib
os.environ['MPLBACKEND'] = 'AGG'
warnings.filterwarnings('ignore')
def _run(pre, code):
    ns = {'__name__': '__main__'}
    for p in pre:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(p, '<앞 예제>', 'exec'), ns)
        except BaseException:
            break
    if 'matplotlib.pyplot' in sys.modules:
        sys.modules['matplotlib.pyplot'].close('all')
    buf, err = io.StringIO(), False
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, '<코드>', 'exec'), ns)
    except BaseException as e:
        err = True
        tb = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == '<코드>']
        msg = 'Traceback (most recent call last):\\n'
        for f in tb:
            msg += f'  File "<코드>", line {f.lineno}\\n    {(code.split(chr(10))[f.lineno - 1] if f.lineno else "").strip()}\\n'
        if isinstance(e, SyntaxError):
            msg = f'  File "<코드>", line {e.lineno}\\n    {(e.text or "").strip()}\\n'
        buf.write(msg + ''.join(traceback.format_exception_only(type(e), e)))
    figs = []
    if 'matplotlib.pyplot' in sys.modules:
        plt = sys.modules['matplotlib.pyplot']
        for n in plt.get_fignums():
            b = io.BytesIO(); plt.figure(n).savefig(b, format='png', dpi=90, bbox_inches='tight')
            figs.append(base64.b64encode(b.getvalue()).decode())
        plt.close('all')
    return json.dumps({'out': buf.getvalue().rstrip('\\n'), 'err': err, 'figs': figs})
`);
        res(py);
      } catch (e) { pyReady = null; rej(e); }
    };
    s.onerror = () => { pyReady = null; rej(new Error('파이썬을 내려받지 못했어요. 처음 한 번은 인터넷 연결이 필요해요.')); };
    document.head.appendChild(s);
  });
  return pyReady;
}
const loadedPkgs = new Set();
async function runPython(code, pre = []) {
  const py = await loadPy();
  const all = pre.join('\n') + '\n' + code;
  const need = ['pandas', 'sklearn', 'scipy', 'statsmodels', 'matplotlib'].filter(p => new RegExp(`(import|from)\\s+${p}`).test(all) && !loadedPkgs.has(p));
  if (need.length) toast(`${need.join(', ')} 준비 중… 처음 한 번만 내려받아요`, 8000);
  await py.loadPackagesFromImports(all);
  need.forEach(p => loadedPkgs.add(p));
  const r = JSON.parse(py.globals.get('_run')(py.toPy(pre), code));
  $('#toast').hidden = true;
  return r;
}

// ───────── 장 퀴즈 ─────────
function renderQuiz(c) {
  $('#title').textContent = `${c.no}장 총정리 퀴즈`;
  const picked = c.quiz.map(() => null);
  const ci = CH.indexOf(c), nextCh = CH[ci + 1];
  view.innerHTML = `<div class="stack"><div class="lhead"><span class="k">${c.no}장 ${c.title}</span><h2>📝 총정리 퀴즈 ${c.quiz.length}문제</h2></div>
    <div class="card quiz" id="qz"></div>
    <div class="nav2"><button data-go="#/c/${c.no}">‹ 목차</button>${nextCh ? `<button class="pri" data-go="#/c/${nextCh.no}">다음 장 ›</button>` : '<button class="pri" data-go="#/cards">🃏 카드 퀴즈 ›</button>'}</div></div>`;
  view.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go));
  const box = $('#qz');
  const draw = () => {
    const answered = picked.every(p => p !== null), right = picked.filter((p, k) => p === c.quiz[k].a).length;
    box.innerHTML = c.quiz.map((q, k) => `<div class="qq"><p>Q${k + 1}. ${q.q}</p><div class="qo">${q.o.map((o, j) => {
      let cls = ''; if (picked[k] !== null) { if (j === q.a) cls = 'right'; else if (j === picked[k]) cls = 'wrong'; }
      return `<button data-q="${k}" data-o="${j}" class="${cls}" ${picked[k] !== null ? 'disabled' : ''}>${'①②③④⑤'[j]} ${o}</button>`;
    }).join('')}</div>${picked[k] !== null ? `<div class="qe ${picked[k] === q.a ? 'ok' : 'no'}">${picked[k] === q.a ? '⭕ 정답!' : '❌ 아쉬워요.'} ${q.e}</div>` : ''}</div>`).join('') +
      (answered ? `<div class="qres">${right === c.quiz.length ? '🎉 모두 맞혔어요! 진도에 기록했어요' : `${right} / ${c.quiz.length} 정답`}</div>
        ${right === c.quiz.length ? '' : '<div style="margin-top:8px"><button class="btnw" id="retry">↺ 틀린 문제 다시 풀기</button></div>'}` : '');
    box.querySelectorAll('[data-q]').forEach(b => b.onclick = () => {
      picked[+b.dataset.q] = +b.dataset.o; draw();
      if (picked.every((p, k) => p === c.quiz[k].a) && !prog['q/' + c.no]) { prog['q/' + c.no] = Date.now(); saveProg(); toast('🎉 퀴즈 완료!'); }
    });
    const r = $('#retry'); if (r) r.onclick = () => { picked.forEach((p, k) => { if (p !== c.quiz[k].a) picked[k] = null; }); draw(); };
  };
  draw();
}

// ───────── 용어 찾기 ─────────
let dictQ = '', dictCh = '';
function renderDict() {
  $('#title').textContent = '용어 찾기';
  view.innerHTML = `<div class="stack">
    <input id="dq" class="search" type="search" placeholder="한글·영어로 찾기 (예: 평균, recall, axis)" value="${esc(dictQ)}" autocomplete="off">
    <div class="chips" id="dch"><button data-ch="" class="${dictCh ? '' : 'on'}">전체</button>${CH.map(c => `<button data-ch="${c.no}" class="${dictCh === c.no ? 'on' : ''}">${c.no} ${c.title.replace(/ ?용어$/, '').replace(/\(.*\)/, '')}</button>`).join('')}</div>
    <div id="dlist" class="stack"></div></div>`;
  const draw = () => {
    const q = dictQ.trim().toLowerCase();
    const list = TERMS.filter(t => (!dictCh || t.c.no === dictCh) && (!q || (t.name + ' ' + t.en + ' ' + t.mean).toLowerCase().includes(q)));
    $('#dlist').innerHTML = list.length ? `<p class="muted" style="margin:0;font-size:13px">${list.length}개 용어</p>` + list.map(t => `<button class="term" data-t="${t.id}">
      <span class="tn">${esc(t.name)} ${known(t) ? '<i class="kn">✓</i>' : ''}</span><span class="te">${esc(t.en)}</span><span class="tm">${esc(t.mean)}</span></button>`).join('')
      : '<div class="card muted">찾는 용어가 없어요. 다른 말로 찾아보세요.</div>';
    $('#dlist').querySelectorAll('[data-t]').forEach(b => b.onclick = () => { const t = TERMS.find(x => x.id === b.dataset.t); go(`#/c/${t.c.no}/${t.s.no}`); });
  };
  $('#dq').oninput = e => { dictQ = e.target.value; draw(); };
  $('#dch').querySelectorAll('[data-ch]').forEach(b => b.onclick = () => { dictCh = b.dataset.ch; $('#dch .on').classList.remove('on'); b.classList.add('on'); draw(); });
  draw();
}

// ───────── 카드 퀴즈: 4지선다 10문제 / 플래시카드 ─────────
let cardOpt = { ch: '', dir: 'mean', only: false };
function cardPool() {
  let pool = TERMS.filter(t => !cardOpt.ch || t.c.no === cardOpt.ch);
  if (cardOpt.only) pool = pool.filter(t => !known(t));
  return pool;
}
function renderCards() {
  $('#title').textContent = '카드 퀴즈';
  const nk = TERMS.filter(known).length;
  view.innerHTML = `<div class="stack">
    <div class="card"><b>외운 용어 ${nk} / ${TERMS.length}</b><div class="bar"><i style="width:${nk / TERMS.length * 100}%"></i></div>
      <p class="muted" style="margin:6px 0 0;font-size:13px">맞히거나 '알아요'를 누른 용어는 외운 용어로 기록돼요.</p></div>
    <div class="card opts">
      <label>범위 <select id="och"><option value="">전체 ${TERMS.length}개</option>${CH.map(c => `<option value="${c.no}" ${cardOpt.ch === c.no ? 'selected' : ''}>${c.no}장 ${c.title}</option>`).join('')}</select></label>
      <label>문제 방향 <select id="odir"><option value="mean">뜻을 보고 → 용어 고르기</option><option value="name" ${cardOpt.dir === 'name' ? 'selected' : ''}>용어를 보고 → 뜻 고르기</option></select></label>
      <label class="chk"><input type="checkbox" id="oonly" ${cardOpt.only ? 'checked' : ''}> 아직 못 외운 용어만</label>
    </div>
    <button class="qbtn" id="startq">✏️ 4지선다 10문제 풀기</button>
    <button class="btnw" id="startf">🃏 플래시카드 넘기기 (눌러서 뒤집기)</button>
  </div>`;
  $('#och').onchange = e => cardOpt.ch = e.target.value;
  $('#odir').onchange = e => cardOpt.dir = e.target.value;
  $('#oonly').onchange = e => cardOpt.only = e.target.checked;
  const ready = () => { const p = cardPool(); if (!p.length) { toast('이 범위에는 남은 용어가 없어요 🎉'); return null; } return p; };
  $('#startq').onclick = () => { const p = ready(); if (p) mcq(shuffle(p).slice(0, 10)); };
  $('#startf').onclick = () => { const p = ready(); if (p) flash(shuffle(p)); };
}
function mcq(qs) {
  let k = 0, right = 0; const wrong = [];
  const step = () => {
    if (k >= qs.length) return result();
    const t = qs[k];
    // 오답은 같은 장 용어를 먼저 섞어 쓰면 더 헷갈려서 좋은 연습이 된다
    const others = shuffle(TERMS.filter(x => x !== t && x.c === t.c)).concat(shuffle(TERMS.filter(x => x.c !== t.c)));
    const opts = shuffle([t, ...others.slice(0, 3)]);
    const byName = cardOpt.dir === 'name';
    view.innerHTML = `<div class="stack"><div class="lhead"><span class="k">카드 퀴즈 · ${k + 1} / ${qs.length}</span><h2>${byName ? '이 용어의 뜻은?' : '이 뜻의 용어는?'}</h2></div>
      <div class="card flashq">${byName ? `<b>${esc(t.name)}</b><small>${esc(t.en)}</small>` : esc(t.hint)}</div>
      <div class="qo">${opts.map((o, j) => `<button data-j="${j}">${'①②③④'[j]} ${byName ? esc(o.hint) : esc(o.name)}</button>`).join('')}</div>
      <div id="fb"></div></div>`;
    view.querySelectorAll('[data-j]').forEach(b => b.onclick = () => {
      const o = opts[+b.dataset.j], ok = o === t;
      view.querySelectorAll('[data-j]').forEach(x => { x.disabled = true; if (opts[+x.dataset.j] === t) x.classList.add('right'); });
      if (!ok) b.classList.add('wrong');
      if (ok) { right++; setKnown(t, true); } else { wrong.push(t); setKnown(t, false); }
      $('#fb').innerHTML = `<div class="qe ${ok ? 'ok' : 'no'}">${ok ? '⭕ 정답!' : '❌ 아쉬워요.'} <b>${esc(t.name)}</b> = ${esc(t.mean)}</div>
        <div class="nav2" style="margin-top:10px"><button data-go="#/c/${t.c.no}/${t.s.no}">설명 보기</button><button class="pri" id="nx">${k + 1 < qs.length ? '다음 문제 ›' : '결과 보기 ›'}</button></div>`;
      $('#fb [data-go]').onclick = e => go(e.target.dataset.go);
      $('#nx').onclick = () => { k++; step(); window.scrollTo(0, 0); };
    });
  };
  const result = () => {
    view.innerHTML = `<div class="stack"><div class="card" style="text-align:center"><h2 style="margin:4px 0">${right === qs.length ? '🎉' : '👍'} ${right} / ${qs.length} 정답</h2>
      <p class="muted" style="margin:0">외운 용어 ${TERMS.filter(known).length} / ${TERMS.length}</p></div>
      ${wrong.length ? `<div class="card"><h3 style="margin:0 0 6px">다시 볼 용어</h3>${wrong.map(t => `<button class="term" data-t="${t.id}"><span class="tn">${esc(t.name)}</span><span class="tm">${esc(t.mean)}</span></button>`).join('')}</div>` : ''}
      <div class="nav2">${wrong.length ? '<button id="again">틀린 것만 다시</button>' : ''}<button class="pri" id="menu">카드 퀴즈 처음으로</button></div></div>`;
    view.querySelectorAll('[data-t]').forEach(b => b.onclick = () => { const t = TERMS.find(x => x.id === b.dataset.t); go(`#/c/${t.c.no}/${t.s.no}`); });
    const a = $('#again'); if (a) a.onclick = () => mcq(shuffle(wrong));
    $('#menu').onclick = renderCards;
  };
  step();
}
function flash(list) {
  let k = 0, flipped = false;
  const draw = () => {
    if (k >= list.length) { toast('카드를 다 넘겼어요 🎉'); return renderCards(); }
    const t = list[k];
    view.innerHTML = `<div class="stack"><div class="lhead"><span class="k">플래시카드 · ${k + 1} / ${list.length}</span><h2>카드를 눌러 뒤집어 보세요</h2></div>
      <button class="flash ${flipped ? 'back' : ''}" id="fc">${flipped
        ? `<b>${esc(t.name)}</b><span class="en">${esc(t.en)}</span><span>${esc(t.mean)}</span>`
        : `<span class="muted">${cardOpt.dir === 'name' ? '이 용어의 뜻은?' : '이 뜻의 용어는?'}</span><b>${cardOpt.dir === 'name' ? esc(t.name) : esc(t.hint)}</b>`}</button>
      <div class="nav2"><button id="no">🤔 모르겠어요</button><button class="pri" id="yes">😀 알아요</button></div>
      <button class="btnw" data-go="#/c/${t.c.no}/${t.s.no}">이 용어 설명 보기</button></div>`;
    $('#fc').onclick = () => { flipped = !flipped; draw(); };
    $('#yes').onclick = () => { setKnown(t, true); k++; flipped = false; draw(); };
    $('#no').onclick = () => { setKnown(t, false); list.push(t); k++; flipped = false; draw(); };   // 모르는 카드는 뒤에 다시 나옴
    view.querySelector('[data-go]').onclick = e => go(e.target.dataset.go);
  };
  draw();
}

// ───────── 사용법 ─────────
function renderHelp() {
  $('#title').textContent = '사용법';
  const installed = matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  const sec = (t, b) => `<div class="card help"><h3>${t}</h3>${b}</div>`;
  view.innerHTML = `<div class="stack">
    ${sec('📚 이렇게 공부해요', `<ol>
      <li><b>학습</b> 탭에서 1장부터 차례로 엽니다. <b>▶ 이어서 학습하기</b>를 누르면 안 본 곳으로 바로 가요.</li>
      <li>용어마다 <b>한 줄 뜻 → 쉬운 설명·비유 → 그림 → 예제 코드</b> 순서예요. 그림을 누르면 크게 보여요.</li>
      <li>절을 열면 읽음(✓)으로 기록되고, 장 끝 <b>총정리 퀴즈</b>를 모두 맞히면 그 장이 완료돼요.</li></ol>`)}
    ${sec('🔍 용어 찾기 · 🃏 카드 퀴즈', `<ul>
      <li><b>용어 찾기</b>: 한글이나 영어로 검색하고, 누르면 설명으로 바로 가요. 분석하다 모르는 말이 나오면 여기서 찾으세요.</li>
      <li><b>카드 퀴즈</b>: 뜻↔용어 4지선다 10문제, 또는 플래시카드로 외워요. 맞히거나 '알아요'를 누른 용어는 <b>외운 용어 ✓</b>로 기록돼요.</li>
      <li>'아직 못 외운 용어만'을 켜면 모르는 것만 골라 연습할 수 있어요.</li></ul>`)}
    ${sec('▶ 예제 코드 실행', `<ul>
      <li>코드 상자는 <b>직접 고칠 수 있어요.</b> 숫자를 바꾸고 <b>▶ 실행</b>을 눌러 보세요. 그래프는 결과 창에 그림으로 나와요.</li>
      <li>처음 실행할 때 파이썬과 pandas 등을 내려받아요(pandas 약 15MB, scikit-learn·scipy 를 쓰는 예제는 30MB 정도 더). <b>와이파이에서</b> 한 번 실행해 두면 그다음부터는 인터넷 없이도 돼요.</li>
      <li>'앞 예제에 이어서 실행' 표시가 있는 코드는 같은 장 앞쪽 예제를 자동으로 먼저 실행해요(노트북처럼).</li>
      <li>앱의 pandas 는 2.x 버전이라 교안(pandas 3)과 자료형 표시가 조금 다를 수 있어요. 예: 글자 열이 <code>str</code> 대신 <code>object</code>.</li></ul>`)}
    ${sec('📲 앱으로 설치 · 오프라인', `<ul>
      <li>${installed ? '✅ 지금 <b>앱으로 실행 중</b>이에요.' : 'Chrome: 위쪽 <b>[설치]</b> 안내 또는 <b>⋮ → 앱 설치</b> · 아이폰 Safari: <b>공유 → 홈 화면에 추가</b>'}</li>
      <li>카카오톡에서 링크를 열면 자동으로 Chrome(아이폰은 Safari)으로 넘어가요.</li>
      <li>새 용어가 추가되면 인터넷이 될 때 앱을 열면 <b>자동으로 업데이트</b>돼요. 진도는 그대로 남아요.</li></ul>`)}
    ${sec('💾 진도 기록', `<ul><li>진도와 외운 용어는 <b>이 폰의 이 브라우저</b>에만 저장돼요.</li></ul>
      <div style="margin-top:10px"><button class="btnw" id="reset">진도 기록 지우기</button></div>`)}
    <p class="muted" style="text-align:center;font-size:13px">${CH.length}개 장 · 용어 ${TERMS.length}개 · 예제 ${CODE.length}개 · 퀴즈 ${CH.reduce((a, c) => a + c.quiz.length, 0)}문제<br>
      <a href="https://github.com/sinaboro/data-terms-lab" target="_blank" rel="noopener">교안 PDF (GitHub)</a></p>
  </div>`;
  $('#reset').onclick = () => { if (confirm('진도와 외운 용어 기록을 모두 지울까요?')) { prog = {}; saveProg(); toast('진도 기록을 지웠어요'); } };
}

// ───────── 앱 설치 · 오프라인 ─────────
// 카카오톡 안에서 열면 바깥 브라우저로 넘기고, Chrome 은 [설치] 버튼, 아이폰은 홈 화면 추가 안내
if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
(() => {
  const bar = $('#inst'), msg = $('#instMsg'), btn = $('#instGo');
  const ua = navigator.userAgent;
  const standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  const kakao = /KAKAOTALK/i.test(ua), android = /Android/i.test(ua);
  const ios = /iP(hone|ad|od)/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const inApp = kakao || /NAVER|Instagram|FBAN|FBAV|Line\//i.test(ua);
  const DISMISS = 'data-terms-install-dismissed';
  const show = (text, label, onGo) => { msg.innerHTML = text; btn.hidden = !label; btn.textContent = label || ''; btn.onclick = onGo || null; bar.hidden = false; };
  const dismissed = () => { try { return localStorage.getItem(DISMISS) === '1'; } catch (e) { return false; } };
  $('#instX').onclick = () => { bar.hidden = true; try { localStorage.setItem(DISMISS, '1'); } catch (e) {} };
  if (standalone) return;
  const openOutside = () => {
    const url = location.href.split('#')[0];
    if (kakao) location.href = 'kakaotalk://web/openExternal?url=' + encodeURIComponent(url);
    else if (android) location.href = `intent://${location.host}${location.pathname}#Intent;scheme=https;package=com.android.chrome;end`;
  };
  if (inApp) {
    show(ios ? '📲 앱으로 설치하려면 <b>Safari</b>에서 열어야 해요.' : '📲 앱으로 설치하려면 <b>Chrome</b>에서 열어야 해요.', ios ? 'Safari로 열기' : 'Chrome으로 열기', openOutside);
    let jumped = false;
    try { jumped = sessionStorage.getItem('kakaoJump') === '1'; sessionStorage.setItem('kakaoJump', '1'); } catch (e) {}
    if (kakao && !jumped) setTimeout(openOutside, 300);
    return;
  }
  let deferred = null;
  addEventListener('beforeinstallprompt', e => {
    e.preventDefault(); deferred = e;
    if (dismissed()) return;
    show('📲 홈 화면에 <b>앱으로 설치</b>하면 인터넷 없이도 공부할 수 있어요.', '설치', async () => {
      deferred.prompt();
      const r = await deferred.userChoice.catch(() => ({}));
      deferred = null; bar.hidden = true;
      if (r.outcome === 'accepted') toast('설치했어요. 홈 화면의 데이터용어 아이콘으로 여세요.');
    });
  });
  addEventListener('appinstalled', () => { bar.hidden = true; });
  if (ios && !dismissed()) show('📲 아래 <b>공유 버튼</b> → <b>홈 화면에 추가</b>를 누르면 앱처럼 쓸 수 있어요.');
})();

route();

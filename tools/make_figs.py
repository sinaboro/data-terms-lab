"""
용어 설명 그림 만들기: guide/figs/*.png (교안 PDF 와 앱이 함께 쓴다)

사용법 (저장소 맨 위 폴더에서):
    pip install matplotlib numpy scikit-learn
    python tools/make_figs.py
모든 그림은 같은 씨앗(seed)으로 만들어 매번 똑같이 나온다.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'guide', 'figs')
os.makedirs(OUT, exist_ok=True)
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']   # 한글 글꼴
plt.rcParams['axes.unicode_minus'] = False                       # - 기호 깨짐 방지
plt.rcParams['axes.spines.top'] = plt.rcParams['axes.spines.right'] = False
BLUE, ORANGE, GREEN, RED, GRAY = '#2f6fdb', '#e8740c', '#1f8a55', '#c0392b', '#8a93a6'
rng = np.random.default_rng(7)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=130)
    plt.close(fig)
    print(name)


# 평균·중앙값·최빈값: 오른쪽으로 치우친 소득 분포
def mean_median_mode():
    x = np.round(rng.lognormal(5.6, 0.45, 600), -1)
    vals, cnt = np.unique(np.round(x, -1), return_counts=True)
    mode = vals[cnt.argmax()]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.hist(x, bins=40, color='#cfdcf5', edgecolor='white')
    for v, c, t in [(mode, GREEN, f'최빈값 {mode:.0f}'), (np.median(x), ORANGE, f'중앙값 {np.median(x):.0f}'), (x.mean(), RED, f'평균 {x.mean():.0f}')]:
        ax.axvline(v, color=c, lw=2.2); ax.text(v + 8, ax.get_ylim()[1] * .9, t, color=c, fontsize=10, fontweight='bold')
    ax.set_title('월 용돈 분포 (오른쪽 꼬리가 긴 분포)'); ax.set_xlabel('용돈(천 원)'); ax.set_ylabel('사람 수')
    save(fig, 'mean_median_mode')


# 분산·표준편차: 평균은 같고 퍼진 정도가 다른 두 반
def variance():
    a, b = rng.normal(70, 4, 300), rng.normal(70, 13, 300)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.hist(a, bins=30, alpha=.7, color=BLUE, label=f'A반  표준편차 {a.std():.1f} (고르게 비슷)')
    ax.hist(b, bins=30, alpha=.55, color=ORANGE, label=f'B반  표준편차 {b.std():.1f} (넓게 퍼짐)')
    ax.axvline(70, color='k', ls='--', lw=1.2); ax.text(70.5, ax.get_ylim()[1] * .92, '두 반 평균 70점', fontsize=9.5)
    ax.legend(frameon=False, fontsize=9.5); ax.set_xlabel('점수'); ax.set_ylabel('학생 수'); ax.set_title('평균은 같아도 퍼진 정도가 다르다')
    save(fig, 'variance')


# 사분위수와 박스플롯
def quartile_box():
    x = np.append(rng.normal(60, 10, 60), [105, 110])
    q1, q2, q3 = np.percentile(x, [25, 50, 75]); iqr = q3 - q1
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.boxplot(x, vert=False, widths=.5, patch_artist=True, boxprops=dict(facecolor='#dfe8fb', color=BLUE), medianprops=dict(color=ORANGE, lw=2.5),
               flierprops=dict(marker='o', markerfacecolor=RED, markeredgecolor=RED))
    for v, t in [(q1, 'Q1\n(25%)'), (q2, 'Q2 중앙값\n(50%)'), (q3, 'Q3\n(75%)')]:
        ax.annotate(t, (v, 1.27), ha='center', fontsize=9.5, color='#1f2a44')
    ax.annotate('IQR = Q3 - Q1\n(가운데 50%)', ((q1 + q3) / 2, .62), ha='center', fontsize=9.5, color=BLUE)
    ax.annotate('이상치', (107.5, 1.12), ha='center', color=RED, fontsize=10, fontweight='bold')
    ax.set_yticks([]); ax.set_xlabel('점수'); ax.set_ylim(.4, 1.5); ax.set_title('사분위수와 박스플롯: 상자 = 가운데 50%, 점 = 이상치')
    save(fig, 'quartile_box')


# 상관계수: 양의 상관 / 상관 없음 / 음의 상관
def correlation():
    fig, axs = plt.subplots(1, 3, figsize=(8.4, 2.9))
    x = rng.uniform(0, 10, 80)
    for ax, y, t in [(axs[0], 2 * x + rng.normal(0, 2.5, 80), '양의 상관'), (axs[1], rng.uniform(0, 20, 80), '상관 거의 없음'), (axs[2], 20 - 1.8 * x + rng.normal(0, 3, 80), '음의 상관')]:
        r = np.corrcoef(x, y)[0, 1]
        ax.scatter(x, y, s=14, color=BLUE, alpha=.75); ax.set_title(f'{t}\nr = {r:.2f}', fontsize=10.5); ax.set_xticks([]); ax.set_yticks([])
    save(fig, 'correlation')


# 왜도: 왼쪽 꼬리 / 대칭 / 오른쪽 꼬리
def skewness():
    from scipy.stats import skew
    fig, axs = plt.subplots(1, 3, figsize=(8.4, 2.7))
    data = [100 - rng.gamma(2, 8, 800), rng.normal(50, 10, 800), rng.gamma(2, 8, 800)]
    for ax, d, t in zip(axs, data, ['왼쪽 꼬리 (음의 왜도)', '좌우 대칭 (왜도 0)', '오른쪽 꼬리 (양의 왜도)']):
        ax.hist(d, bins=30, color=ORANGE if '양' in t else BLUE if '음' in t else GREEN, alpha=.8)
        ax.set_title(f'{t}\n왜도 = {skew(d):.2f}', fontsize=10); ax.set_yticks([])
    save(fig, 'skewness')


# 첨도: 뾰족함·꼬리 두께
def kurtosis():
    from scipy.stats import kurtosis as kt
    fig, ax = plt.subplots(figsize=(7, 3))
    for d, c, t in [(rng.laplace(0, 1, 6000), RED, '뾰족하고 꼬리가 두꺼움'), (rng.normal(0, 1.41, 6000), BLUE, '정규분포'), (rng.uniform(-2.4, 2.4, 6000), GREEN, '납작함')]:
        ax.hist(d, bins=60, range=(-6, 6), density=True, histtype='step', lw=2, color=c, label=f'{t} (첨도 {kt(d):.1f})')
    ax.legend(frameon=False, fontsize=9.5); ax.set_yticks([]); ax.set_title('첨도: 분포가 얼마나 뾰족하고 꼬리가 두꺼운가 (정규분포 = 0 기준)')
    save(fig, 'kurtosis')


# 정규화 vs 표준화: 단위가 다른 두 변수
def scaling():
    age = rng.normal(35, 9, 200); income = rng.normal(4000, 900, 200)
    fig, axs = plt.subplots(1, 3, figsize=(8.6, 2.9))
    axs[0].scatter(age, income, s=10, color=GRAY); axs[0].set_title('원래 값\n(나이 20~60, 소득 2000~6000)', fontsize=10)
    z = lambda v: (v - v.mean()) / v.std(); m = lambda v: (v - v.min()) / (v.max() - v.min())
    axs[1].scatter(m(age), m(income), s=10, color=ORANGE); axs[1].set_title('정규화 (Min-Max)\n둘 다 0 ~ 1', fontsize=10)
    axs[2].scatter(z(age), z(income), s=10, color=BLUE); axs[2].set_title('표준화 (Z-score)\n평균 0, 표준편차 1', fontsize=10)
    axs[2].axhline(0, color='k', lw=.6); axs[2].axvline(0, color='k', lw=.6)
    for ax in axs: ax.set_xlabel('나이'); axs[0].set_ylabel('소득')
    save(fig, 'scaling')


# 히스토그램과 정규분포
def histogram():
    s = rng.normal(72, 11, 300).clip(20, 100)
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.hist(s, bins=[30, 40, 50, 60, 70, 80, 90, 100], color='#cfdcf5', edgecolor=BLUE)
    ax.set_xticks([30, 40, 50, 60, 70, 80, 90, 100]); ax.set_xlabel('점수 구간'); ax.set_ylabel('학생 수(빈도)')
    ax.set_title('히스토그램: 구간마다 몇 명인지 막대로')
    save(fig, 'histogram')


def normal_dist():
    x = np.linspace(-4, 4, 400); y = np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)
    fig, ax = plt.subplots(figsize=(7, 2.9))
    ax.plot(x, y, color=BLUE, lw=2.5)
    for k, a in [(1, .35), (2, .18), (3, .08)]:
        ax.fill_between(x, y, where=(abs(x) <= k), color=BLUE, alpha=a)
    for k, t in [(0.5, '68%'), (1.5, '95%'), (2.5, '99.7%')]:
        ax.text(k, .03 + (2.6 - k) * .05, t, fontsize=9.5, color='#1f2a44')
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3]); ax.set_xticklabels(['-3σ', '-2σ', '-1σ', '평균', '+1σ', '+2σ', '+3σ']); ax.set_yticks([])
    ax.set_title('정규분포: 평균을 중심으로 좌우 대칭인 종 모양')
    save(fig, 'normal_dist')


def scatter():
    h = rng.uniform(0, 10, 50); sc = 40 + 5 * h + rng.normal(0, 6, 50)
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.scatter(h, sc, color=BLUE, s=24); ax.set_xlabel('공부 시간(시간)'); ax.set_ylabel('점수')
    ax.set_title('산점도: 점 하나 = 학생 한 명')
    save(fig, 'scatter')


def heatmap():
    names = ['공부시간', '점수', '수면시간', '게임시간']
    c = np.array([[1, .82, -.15, -.55], [.82, 1, .05, -.6], [-.15, .05, 1, -.2], [-.55, -.6, -.2, 1]])
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    im = ax.imshow(c, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_xticks(range(4)); ax.set_yticks(range(4)); ax.set_xticklabels(names); ax.set_yticklabels(names)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f'{c[i, j]:.2f}', ha='center', va='center', color='white' if abs(c[i, j]) > .5 else 'black')
    fig.colorbar(im, shrink=.8); ax.set_title('상관계수 히트맵: 빨강 = 양, 파랑 = 음')
    save(fig, 'heatmap')


# 과소적합 / 적당 / 과적합
def fitting():
    x = np.sort(rng.uniform(0, 1, 18)); y = np.sin(2 * np.pi * x) + rng.normal(0, .25, 18); xs = np.linspace(0, 1, 300)
    fig, axs = plt.subplots(1, 3, figsize=(8.6, 2.8))
    for ax, d, t in zip(axs, [1, 3, 15], ['과소적합\n(너무 단순)', '적당함', '과적합\n(점을 외워 버림)']):
        p = np.polyfit(x, y, d); ax.scatter(x, y, s=16, color=GRAY); ax.plot(xs, np.clip(np.polyval(p, xs), -2, 2), color=RED if d == 15 else GREEN if d == 3 else ORANGE, lw=2)
        ax.set_title(t, fontsize=10.5); ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(-2, 2)
    save(fig, 'fitting')


def split():
    fig, ax = plt.subplots(figsize=(7, 1.6))
    for x0, w, c, t in [(0, 60, BLUE, '훈련 데이터 60%\n(공부용 문제집)'), (60, 20, ORANGE, '검증 20%\n(모의고사)'), (80, 20, GREEN, '테스트 20%\n(진짜 시험)')]:
        ax.barh(0, w, left=x0, color=c, edgecolor='white'); ax.text(x0 + w / 2, 0, t, ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    ax.set_xlim(0, 100); ax.axis('off')
    save(fig, 'split')


def confusion():
    fig, ax = plt.subplots(figsize=(5.4, 4))
    cells = [[('TP\n진짜 양성', '스팸을 스팸으로', GREEN), ('FN\n놓친 양성', '스팸을 정상으로', RED)],
             [('FP\n가짜 양성', '정상을 스팸으로', RED), ('TN\n진짜 음성', '정상을 정상으로', GREEN)]]
    for i in range(2):
        for j in range(2):
            t, s, c = cells[i][j]
            ax.add_patch(plt.Rectangle((j, 1 - i), 1, 1, color=c, alpha=.18)); ax.text(j + .5, 1.62 - i, t, ha='center', va='center', fontsize=12, fontweight='bold', color=c)
            ax.text(j + .5, 1.25 - i, s, ha='center', fontsize=9.5)
    ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.set_xticks([.5, 1.5]); ax.set_xticklabels(['예측: 스팸', '예측: 정상']); ax.set_yticks([1.5, .5]); ax.set_yticklabels(['실제: 스팸', '실제: 정상'])
    ax.xaxis.tick_top(); ax.set_title('혼동행렬 (스팸 메일 분류)', pad=26)
    save(fig, 'confusion')


def roc():
    t = np.linspace(0, 1, 100)
    fig, ax = plt.subplots(figsize=(4.6, 4))
    ax.plot(t, t ** .25, color=GREEN, lw=2.5, label='좋은 모델 (AUC 0.9 근처)'); ax.plot(t, t ** .6, color=ORANGE, lw=2.2, label='보통 모델'); ax.plot(t, t, 'k--', lw=1.2, label='찍기 (AUC 0.5)')
    ax.fill_between(t, t ** .25, alpha=.12, color=GREEN); ax.set_xlabel('거짓 양성 비율 (FPR)'); ax.set_ylabel('참 양성 비율 (TPR = Recall)')
    ax.legend(frameon=False, fontsize=9, loc='lower right'); ax.set_title('ROC 곡선: 왼쪽 위로 붙을수록 좋다\n(아래 넓이 = AUC)', fontsize=10.5)
    save(fig, 'roc')


# 회귀: 절편·기울기(계수)·잔차
def regression():
    x = np.array([1, 2, 3, 4, 5, 6, 7]); y = np.array([3.2, 4.6, 7.4, 8.1, 10.9, 12.2, 15.1]); b1, b0 = np.polyfit(x, y, 1)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    xs = np.linspace(0, 7.5, 50); ax.plot(xs, b0 + b1 * xs, color=BLUE, lw=2.2, label=f'회귀선 y = {b1:.2f}x + {b0:.2f}')
    ax.scatter(x, y, color=ORANGE, zorder=3, s=36, label='실제 데이터')
    for xi, yi in zip(x, y): ax.plot([xi, xi], [yi, b0 + b1 * xi], color=RED, lw=1.2, ls=':')
    ax.scatter([0], [b0], color=GREEN, s=60, zorder=4); ax.annotate(f'절편 {b0:.2f}\n(x=0 일 때 y)', (0, b0), (0.4, b0 + 3.2), arrowprops=dict(arrowstyle='->', color=GREEN), color=GREEN, fontsize=9.5)
    ax.annotate('', (5, b0 + b1 * 5), (4, b0 + b1 * 4), arrowprops=dict(arrowstyle='-', color='k'))
    ax.plot([4, 5], [b0 + b1 * 4] * 2, 'k', lw=1); ax.plot([5, 5], [b0 + b1 * 4, b0 + b1 * 5], 'k', lw=1)
    ax.text(5.08, b0 + b1 * 4.4, f'x 가 1 늘면\ny 가 {b1:.2f} (계수=기울기)', fontsize=9)
    ax.text(6.05, 10.2, '빨간 점선 = 잔차\n(실제 - 예측)', color=RED, fontsize=9)
    ax.set_xlim(-0.2, 7.6); ax.set_ylim(0, 17); ax.set_xlabel('광고비'); ax.set_ylabel('매출'); ax.legend(frameon=False, fontsize=9, loc='upper left')
    save(fig, 'regression')


def kmeans():
    from sklearn.cluster import KMeans
    pts = np.vstack([rng.normal(c, .6, (40, 2)) for c in [(2, 2), (6, 3), (4, 7)]])
    km = KMeans(3, n_init=10, random_state=0).fit(pts)
    fig, ax = plt.subplots(figsize=(5.4, 4))
    for k, c in enumerate([BLUE, ORANGE, GREEN]):
        ax.scatter(*pts[km.labels_ == k].T, s=16, color=c, alpha=.8)
    ax.scatter(*km.cluster_centers_.T, marker='X', s=200, color='k', label='중심점 (centroid)'); ax.legend(frameon=False)
    ax.set_title('K-Means (K=3): 가까운 점끼리 3개 그룹'); ax.set_xticks([]); ax.set_yticks([])
    save(fig, 'kmeans')


def elbow():
    from sklearn.cluster import KMeans
    pts = np.vstack([rng.normal(c, .6, (40, 2)) for c in [(2, 2), (6, 3), (4, 7)]])
    ks = range(1, 9); inertia = [KMeans(k, n_init=10, random_state=0).fit(pts).inertia_ for k in ks]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(ks, inertia, 'o-', color=BLUE, lw=2); ax.scatter([3], [inertia[2]], s=180, facecolor='none', edgecolor=RED, lw=2.5)
    ax.annotate('팔꿈치! K=3', (3, inertia[2]), (4.3, inertia[2] + max(inertia) * .25), arrowprops=dict(arrowstyle='->', color=RED), color=RED, fontsize=11, fontweight='bold')
    ax.set_xlabel('클러스터 개수 K'); ax.set_ylabel('그룹 안의 흩어짐 (inertia)'); ax.set_title('엘보우 그래프: 꺾이는 지점의 K 를 고른다')
    save(fig, 'elbow')


# DataFrame 의 axis 방향: axis=0 은 위→아래로 내려가며 계산(열마다 결과), axis=1 은 왼→오른쪽(행마다 결과)
def axis():
    fig, ax = plt.subplots(figsize=(7, 3.8)); ax.axis('off')
    cols = ['국어', '영어', '수학']; rows = ['민수', '지아', '서준']
    data = np.array([[80, 90, 70], [60, 85, 95], [75, 70, 88]])
    for j, c in enumerate(cols): ax.text(1.2 + j, 3.55, c, ha='center', fontweight='bold')
    for i, r in enumerate(rows):
        ax.text(.45, 2.9 - i, r, ha='center', fontweight='bold')
        for j in range(3):
            ax.add_patch(plt.Rectangle((.75 + j, 2.55 - i), .9, .7, color='#eef2fb', ec=GRAY)); ax.text(1.2 + j, 2.9 - i, data[i][j], ha='center', va='center')
        ax.add_patch(plt.Rectangle((4.05, 2.55 - i), .9, .7, color='#dfe8fb', ec=BLUE)); ax.text(4.5, 2.9 - i, data[i].sum(), ha='center', va='center', color=BLUE, fontweight='bold')
    for j in range(3):
        ax.add_patch(plt.Rectangle((.75 + j, -.25), .9, .7, color='#fbe4e1', ec=RED)); ax.text(1.2 + j, .1, data[:, j].sum(), ha='center', va='center', color=RED, fontweight='bold')
    ax.annotate('', (3.95, 2.9), (3.72, 2.9), arrowprops=dict(arrowstyle='->', color=BLUE, lw=2.5))
    ax.text(4.5, 3.55, 'axis=1 →\n학생별 합계', ha='center', color=BLUE, fontsize=9.5, fontweight='bold')
    ax.annotate('', (1.2, .5), (1.2, .62), arrowprops=dict(arrowstyle='->', color=RED, lw=2.5))
    ax.text(-.05, .1, 'axis=0 ↓\n과목별 합계', ha='center', va='center', color=RED, fontsize=9.5, fontweight='bold')
    ax.set_xlim(-.6, 5.2); ax.set_ylim(-.4, 3.95)
    save(fig, 'axis')


def cohort():
    months = ['1월 가입', '2월 가입', '3월 가입', '4월 가입']
    r = np.array([[100, 45, 32, 26], [100, 50, 38, np.nan], [100, 58, np.nan, np.nan], [100, np.nan, np.nan, np.nan]])
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.imshow(np.nan_to_num(r, nan=0), cmap='Blues', vmin=0, vmax=100)
    for i in range(4):
        for j in range(4):
            if not np.isnan(r[i, j]): ax.text(j, i, f'{r[i, j]:.0f}%', ha='center', va='center', color='white' if r[i, j] > 60 else 'black')
    ax.set_xticks(range(4)); ax.set_xticklabels(['가입 달', '1달 뒤', '2달 뒤', '3달 뒤']); ax.set_yticks(range(4)); ax.set_yticklabels(months)
    ax.set_title('코호트 분석: 가입 달별로 남아 있는 비율(유지율)')
    save(fig, 'cohort')


def funnel():
    steps = ['방문', '상품 보기', '장바구니', '결제']; n = [1000, 420, 150, 60]
    fig, ax = plt.subplots(figsize=(6.6, 3))
    for i, (s, v) in enumerate(zip(steps, n)):
        ax.barh(i, v, left=(1000 - v) / 2, color=BLUE, alpha=1 - i * .18); ax.text(500, i, f'{s} {v}명', ha='center', va='center', color='white', fontweight='bold')
    ax.invert_yaxis(); ax.axis('off'); ax.set_title('전환 깔때기: 방문 1000명 중 60명 결제 → 전환율 6%')
    save(fig, 'funnel')


def ab_test():
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(['A안\n(초록 버튼)', 'B안\n(주황 버튼)'], [4.1, 5.6], color=[GREEN, ORANGE], width=.5)
    for i, v in enumerate([4.1, 5.6]): ax.text(i, v + .1, f'{v}%', ha='center', fontweight='bold')
    ax.set_ylabel('전환율(%)'); ax.set_ylim(0, 7); ax.set_title('A/B 테스트: 사용자를 반씩 나눠 비교')
    save(fig, 'ab_test')


def flow():
    steps = [('01 데이터 수집', 'CSV, SQL'), ('02 전처리', '결측치·인코딩'), ('03 탐색(EDA)', '분포·상관'),
             ('04 피처 엔지니어링', '변수 만들기'), ('05 모델 학습', '분류·회귀·군집'), ('06 평가·해석', 'Accuracy·RMSE')]
    fig, ax = plt.subplots(figsize=(9, 2.3)); ax.axis('off'); ax.set_xlim(0, 6); ax.set_ylim(0, 1)
    for i, (t, s) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((i + .06, .2), .8, .6, boxstyle='round,pad=0.02', color=BLUE if i % 2 == 0 else '#4a84e8'))
        ax.text(i + .46, .58, t, ha='center', va='center', color='white', fontsize=9, fontweight='bold'); ax.text(i + .46, .36, s, ha='center', va='center', color='white', fontsize=8.2)
        if i < 5: ax.annotate('', (i + 1.06, .5), (i + .88, .5), arrowprops=dict(arrowstyle='->', color=ORANGE, lw=2))
    save(fig, 'flow')


def clf_reg():
    fig, axs = plt.subplots(1, 2, figsize=(8, 3))
    a = rng.normal((3, 3), .8, (40, 2)); b = rng.normal((6, 6), .8, (40, 2))
    axs[0].scatter(*a.T, color=BLUE, s=16, label='합격'); axs[0].scatter(*b.T, color=ORANGE, s=16, label='불합격'); axs[0].plot([1, 8], [8, 1], 'k--')
    axs[0].legend(frameon=False, fontsize=9); axs[0].set_title('분류: 어느 그룹? (정답이 범주)', fontsize=10.5)
    x = rng.uniform(0, 10, 40); axs[1].scatter(x, 3 * x + rng.normal(0, 3, 40), color=BLUE, s=16); axs[1].plot([0, 10], [0, 30], color=RED)
    axs[1].set_title('회귀: 얼마? (정답이 숫자)', fontsize=10.5)
    for ax in axs: ax.set_xticks([]); ax.set_yticks([])
    save(fig, 'clf_reg')


# 머신러닝 모델 지도: 지도학습(분류·회귀) / 비지도학습(군집·차원 축소·기타)
def ml_map():
    fig, ax = plt.subplots(figsize=(9, 4.1)); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0.45, 5.9)
    def box(x, y, w, h, t, c, fc='white', fs=9.5, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03', fc=fc, ec=c, lw=1.6))
        ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, color=c if fc == 'white' else 'white', fontweight='bold' if bold else 'normal')
    box(3.6, 5.2, 2.8, .6, '머신러닝', GRAY, GRAY, 12, True)
    box(.4, 4.0, 4.2, .7, '지도학습 (정답 있음)', BLUE, BLUE, 11, True)
    box(5.4, 4.0, 4.2, .7, '비지도학습 (정답 없음)', ORANGE, ORANGE, 11, True)
    for x in (2.5, 7.5): ax.plot([5, x], [5.2, 4.7], color=GRAY, lw=1.5)
    cols = [(.4, '분류 · 회귀 모두', ['선형/로지스틱 회귀', 'K-최근접 이웃(KNN)', '결정 트리', '랜덤 포레스트', '그레이디언트 부스팅', 'SVM', '나이브 베이즈(분류)', '신경망(MLP)'], BLUE),
            (5.4, '군집 · 차원 축소 · 기타', ['K-평균(K-Means)', '계층적 군집', 'DBSCAN', '주성분 분석(PCA)', 't-SNE', '연관 규칙(장바구니)', '이상 탐지'], ORANGE)]
    for x0, head, names, c in cols:
        ax.text(x0 + 2.1, 3.65, head, ha='center', fontsize=9, color=c)
        for k, n in enumerate(names):
            box(x0 + (k % 2) * 2.15, 2.75 - (k // 2) * .72, 2.0, .55, n, c, fs=9)
    save(fig, 'ml_map')


# 지도학습 모델 4개가 같은 데이터를 나누는 방식(결정 경계) 비교
def sup_boundary():
    from sklearn.datasets import make_moons
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.svm import SVC
    X, y = make_moons(200, noise=.25, random_state=0)
    xx, yy = np.meshgrid(np.linspace(-1.6, 2.6, 200), np.linspace(-1.2, 1.7, 200))
    models = [('로지스틱 회귀 (직선)', LogisticRegression()), ('KNN (가까운 이웃)', KNeighborsClassifier(7)),
              ('결정 트리 (계단 모양)', DecisionTreeClassifier(max_depth=5, random_state=0)), ('SVM (부드러운 곡선)', SVC(gamma=2))]
    fig, axs = plt.subplots(1, 4, figsize=(11, 3))
    for ax, (t, m) in zip(axs, models):
        m.fit(X, y); z = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        ax.contourf(xx, yy, z, alpha=.25, cmap='coolwarm'); ax.scatter(*X.T, c=y, cmap='coolwarm', s=10, edgecolor='white', lw=.3)
        ax.set_title(f'{t}\n정확도 {m.score(X, y):.2f}', fontsize=10); ax.set_xticks([]); ax.set_yticks([])
    save(fig, 'sup_boundary')


# 비지도 군집 비교: K-Means 는 동그란 무리, DBSCAN 은 빽빽한 모양을 따라 묶는다 + 계층적 군집 덴드로그램
def unsup_compare():
    from sklearn.datasets import make_moons
    from sklearn.cluster import KMeans, DBSCAN
    from scipy.cluster.hierarchy import dendrogram, linkage
    X, _ = make_moons(200, noise=.06, random_state=1)
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2))
    for ax, (t, lab) in zip(axs[:2], [('K-Means (k=2): 동그랗게 자름', KMeans(2, n_init=10, random_state=0).fit_predict(X)),
                                       ('DBSCAN: 빽빽한 모양을 따라감', DBSCAN(eps=.2).fit_predict(X))]):
        ax.scatter(*X.T, c=lab, cmap='coolwarm', s=12); ax.set_title(t, fontsize=10); ax.set_xticks([]); ax.set_yticks([])
    pts = np.random.default_rng(3).normal(size=(12, 2)) + np.repeat([[0, 0], [4, 4], [0, 5]], 4, axis=0)
    dendrogram(linkage(pts, 'ward'), ax=axs[2], color_threshold=4, above_threshold_color=GRAY)
    axs[2].set_title('계층적 군집: 가까운 것부터 차례로 합침', fontsize=10); axs[2].set_yticks([]); axs[2].set_xlabel('데이터 번호')
    save(fig, 'unsup_compare')


if __name__ == '__main__':
    for f in [mean_median_mode, variance, quartile_box, correlation, skewness, kurtosis, scaling, histogram, normal_dist, scatter, heatmap,
              fitting, split, confusion, roc, regression, kmeans, elbow, axis, cohort, funnel, ab_test, flow, clf_reg,
              ml_map, sup_boundary, unsup_compare]:
        f()

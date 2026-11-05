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


# ───────── 11·12장 인공지능 용어 그림 ─────────
def _box(ax, x, y, w, h, t, c, fill=True, fs=9.5, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03', fc=c if fill else 'white', ec=c, lw=1.6))
    ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, color=tc or ('white' if fill else c), fontweight='bold' if fill else 'normal')


def _arrow(ax, a, b, c=ORANGE):
    ax.annotate('', b, a, arrowprops=dict(arrowstyle='->', color=c, lw=2))


# 사전학습 → 미세조정
def pretrain_finetune():
    fig, ax = plt.subplots(figsize=(9, 3)); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 3.2)
    _box(ax, .1, 1.1, 2.2, 1.0, '아주 많은 글\n(책·뉴스·웹 문서)', GRAY, False)
    _arrow(ax, (2.4, 1.6), (3.1, 1.6))
    _box(ax, 3.2, 1.1, 2.4, 1.0, '사전학습 모델\n(기본 언어 능력)', BLUE)
    ax.text(4.4, 2.45, 'Pre-training: 넓고 다양하게 미리 공부', ha='center', fontsize=9, color=BLUE)
    for k, (t, y) in enumerate([('번역 데이터 → 번역 모델', 2.3), ('요약 데이터 → 요약 모델', 1.35), ('리뷰 데이터 → 감성 분석', .4)]):
        _arrow(ax, (5.7, 1.6), (6.5, y + .3), GREEN)
        _box(ax, 6.55, y, 3.3, .6, t, GREEN, False, 9)
    ax.text(8.2, 3.05, 'Fine-tuning: 하고 싶은 일에 맞춰 추가 학습', ha='center', fontsize=9, color=GREEN)
    save(fig, 'pretrain_finetune')


# 토큰화: 문장을 조각(subword)으로
def tokenize():
    fig, ax = plt.subplots(figsize=(9, 2.6)); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 3)
    ax.text(.1, 2.5, '문장:  "데이터분석은 재미있다"', fontsize=11)
    rows = [('단어 단위', ['데이터분석은', '재미있다'], GRAY), ('subword 조각', ['▁데이터', '분석', '은', '▁재미', '있다'], BLUE)]
    for r, (name, toks, c) in enumerate(rows):
        y = 1.55 - r * 1.0
        ax.text(.1, y + .25, name, fontsize=9.5, color=c, fontweight='bold')
        x = 1.9
        for t in toks:
            w = .35 + .32 * len(t)
            _box(ax, x, y, w, .55, t, c, False, 10); x += w + .2
        ax.text(x + .1, y + .25, f'→ 토큰 {len(toks)}개', fontsize=9.5, color=c)
    save(fig, 'tokenize')


# 임베딩: 뜻이 비슷한 낱말은 가까운 좌표에
def embedding():
    pts = {'왕': (1, 4.2), '여왕': (2.2, 4.5), '남자': (1.1, 2.7), '여자': (2.3, 3.0), '강아지': (5.2, 1.4), '고양이': (5.9, 1.9),
           '사과': (7.6, 4.1), '바나나': (8.3, 3.6), '포도': (7.9, 4.8)}
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for w, (x, y) in pts.items():
        ax.scatter(x, y, s=60, color=BLUE); ax.text(x + .12, y + .12, w, fontsize=10.5)
    for a, b in [('왕', '여왕'), ('남자', '여자')]:
        ax.annotate('', pts[b], pts[a], arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.6))
    for t, (x, y) in [('사람', (1.5, 1.9)), ('동물', (5.4, .6)), ('과일', (7.9, 2.8))]:
        ax.text(x, y, t, fontsize=9, color=GRAY)
    ax.set_xlim(0, 9.5); ax.set_ylim(0, 5.5); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title('임베딩: 낱말을 숫자 좌표(벡터)로 — 뜻이 비슷하면 가깝다', fontsize=10.5)
    save(fig, 'embedding')


# 엔트로피: 확신 vs 갈팡질팡
def entropy():
    fig, axs = plt.subplots(1, 3, figsize=(9, 2.8), sharey=True)
    for ax, (t, p) in zip(axs, [('확신함', [.94, .03, .03]), ('조금 헷갈림', [.6, .3, .1]), ('갈팡질팡', [.34, .33, .33])]):
        p = np.array(p); h = -(p * np.log2(p)).sum()
        ax.bar(['고양이', '강아지', '토끼'], p, color=[BLUE, '#9db8ee', '#c9d7f5'])
        ax.set_title(f'{t}\n엔트로피 {h:.2f}', fontsize=10); ax.set_ylim(0, 1)
    axs[0].set_ylabel('모델이 준 확률')
    save(fig, 'entropy')


# 경사하강법과 학습률: 너무 작음 / 적당 / 너무 큼
def learning_rate():
    f = lambda w: (w - 3) ** 2 + 1
    ws = np.linspace(-2.5, 8.5, 200)
    fig, axs = plt.subplots(1, 3, figsize=(10, 3))
    for ax, (t, lr) in zip(axs, [('학습률 너무 작음: 느림', .03), ('학습률 적당: 빨리 바닥', .3), ('학습률 너무 큼: 튀어 다님', .98)]):
        ax.plot(ws, f(ws), color=GRAY)
        w, path = -1.5, []
        for _ in range(10):
            path.append(w); w = w - lr * 2 * (w - 3)
        path = np.array(path)
        ax.plot(path, f(path), 'o-', color=ORANGE, ms=4, lw=1.2)
        ax.scatter([3], [1], marker='*', s=150, color=GREEN, zorder=5)
        ax.set_title(t, fontsize=10); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel('가중치 w'); ax.set_ylim(0, 35)
    axs[0].set_ylabel('손실(Loss)')
    save(fig, 'learning_rate')


# 옵티마이저 비교: 길쭉한 골짜기에서 SGD / Momentum / Adam 경로
def optimizers():
    a, b = 1.0, 12.0                                   # 손실 = a·x² + b·y² (y 방향이 가파른 골짜기)
    grad = lambda p: np.array([2 * a * p[0], 2 * b * p[1]])
    def run(kind, steps=40):
        p, v, s, m = np.array([-4.5, 1.6]), np.zeros(2), np.zeros(2), np.zeros(2)
        path = [p.copy()]
        for t in range(1, steps + 1):
            g = grad(p)
            if kind == 'SGD':
                p = p - .075 * g
            elif kind == 'Momentum':
                v = .8 * v - .03 * g; p = p + v
            else:                                           # Adam
                m = .9 * m + .1 * g; s = .999 * s + .001 * g * g
                mh, sh = m / (1 - .9 ** t), s / (1 - .999 ** t)
                p = p - .2 * mh / (np.sqrt(sh) + 1e-8)
            path.append(p.copy())
        return np.array(path)
    x, y = np.meshgrid(np.linspace(-5, 2.2, 200), np.linspace(-2, 2, 200))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.contour(x, y, a * x ** 2 + b * y ** 2, levels=15, colors='#d5dae4')
    for kind, c in [('SGD', GRAY), ('Momentum', ORANGE), ('Adam', BLUE)]:
        pth = run(kind); ax.plot(*pth.T, 'o-', ms=2.5, lw=1.3, color=c, label=kind)
    ax.scatter([0], [0], marker='*', s=200, color=GREEN, zorder=5, label='목표(손실 최소)')
    ax.legend(frameon=False, fontsize=9, loc='lower right'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title('옵티마이저마다 골짜기 바닥으로 내려가는 길이 다르다 (40걸음)', fontsize=10.5)
    save(fig, 'optimizers')


# 에포크 · 배치 · 이터레이션
def epoch_batch():
    fig, ax = plt.subplots(figsize=(9, 2.8)); ax.axis('off'); ax.set_xlim(0, 10.4); ax.set_ylim(0, 3)
    ax.text(.1, 2.6, '데이터 1,000개, 배치 크기 100 → 1 에포크 = 10 이터레이션', fontsize=10.5, fontweight='bold')
    for k in range(10):
        _box(ax, .1 + k * 1.02, 1.3, .92, .8, f'배치 {k + 1}\n100개', BLUE if k < 3 else '#9db8ee', fs=8.5)
    ax.text(.1, .85, '배치 1개로 공부하고 가중치를 한 번 고치면 = 이터레이션 1번', fontsize=9.3, color=BLUE)
    ax.text(.1, .35, '배치 10개를 다 돌아 1,000개를 한 번씩 다 보면 = 에포크 1번  (에포크 10 = 이 과정을 10번 반복)', fontsize=9.3, color=ORANGE)
    save(fig, 'epoch_batch')


# 에포크에 따른 손실: 과소적합 → 적당 → 과적합
def epoch_curve():
    e = np.arange(1, 61)
    tr = 2.2 * np.exp(-e / 9) + .15
    va = 2.2 * np.exp(-e / 9) + .3 + .0009 * np.maximum(0, e - 18) ** 2
    fig, ax = plt.subplots(figsize=(7, 3.3))
    ax.plot(e, tr, color=BLUE, label='훈련 손실'); ax.plot(e, va, color=ORANGE, label='검증 손실')
    best = e[va.argmin()]
    ax.axvline(best, color=GREEN, ls='--'); ax.text(best + 1, 2.0, f'여기서 멈춤\n(에포크 {best})', color=GREEN, fontsize=9)
    ax.axvspan(1, 8, color='#e8edf7'); ax.text(2, 2.35, '과소적합', fontsize=9, color=GRAY)
    ax.axvspan(40, 60, color='#fdecea'); ax.text(43, 2.35, '과적합', fontsize=9, color=RED)
    ax.set_xlabel('에포크'); ax.set_ylabel('손실'); ax.legend(frameon=False, loc='center right'); ax.set_ylim(0, 2.6)
    save(fig, 'epoch_curve')


# 순전파 · 역전파
def propagation():
    fig, ax = plt.subplots(figsize=(8.5, 3.6)); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(-.1, 4.3); ax.set_aspect('equal')
    layers = [(1.2, 3, '입력'), (4, 4, '은닉층'), (6.8, 2, '출력')]
    pos = []
    for x, n, t in layers:
        ys = np.linspace(1.2, 3.2, n) if n > 1 else [2]
        pos.append([(x, y) for y in ys]); ax.text(x, 3.55, t, ha='center', fontsize=9.5, color=GRAY)
    for L in range(2):
        for p in pos[L]:
            for q in pos[L + 1]:
                ax.plot([p[0], q[0]], [p[1], q[1]], color='#d5dae4', lw=1)
    for L in pos:
        for x, y in L:
            ax.add_patch(plt.Circle((x, y), .22, color=BLUE, zorder=3))
    _box(ax, 8.0, 1.6, 1.8, .8, '손실\n(틀린 정도)', RED, fs=9)
    _arrow(ax, (1.2, 4.0), (6.8, 4.0), BLUE); ax.text(4, 4.1, '순전파: 입력 → 예측 계산', ha='center', fontsize=9.5, color=BLUE)
    ax.annotate('', (1.2, .65), (8.9, .65), arrowprops=dict(arrowstyle='->', color=RED, lw=2))
    ax.text(5.0, .1, '역전파: 손실을 거꾸로 전해 가중치 고치기', ha='center', fontsize=9.5, color=RED)
    save(fig, 'propagation')


# 온도(Temperature): 다음 낱말 확률이 달라진다
def temperature():
    words = ['맑음', '흐림', '비', '눈', '무지개']
    logit = np.array([3.0, 2.0, 1.2, .3, -.5])
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.9), sharey=True)
    for ax, T in zip(axs, [.3, 1.0, 2.0]):
        p = np.exp(logit / T); p /= p.sum()
        ax.bar(words, p, color=BLUE); ax.set_title(f'Temperature {T}', fontsize=10.5); ax.set_ylim(0, 1)
        for i, v in enumerate(p): ax.text(i, v + .02, f'{v:.2f}', ha='center', fontsize=8)
    axs[0].set_ylabel('다음 낱말 확률'); fig.suptitle('"내일 날씨는 ___"', fontsize=10.5, y=.98)
    save(fig, 'temperature')


# 제로샷 · 원샷 · 퓨샷
def shots():
    fig, ax = plt.subplots(figsize=(9, 2.7)); ax.axis('off'); ax.set_xlim(0, 9.3); ax.set_ylim(0, 3)
    cols = [('Zero-shot', ['리뷰 감정을 분류해 줘', '"배송 빨라요" →'], GRAY), ('One-shot', ['예) "맛없어요" → 부정', '"배송 빨라요" →'], BLUE),
            ('Few-shot', ['예) "맛없어요" → 부정', '예) "최고예요" → 긍정', '예) "그냥 그래요" → 중립', '"배송 빨라요" →'], GREEN)]
    for k, (t, lines, c) in enumerate(cols):
        x = .1 + k * 3.1
        _box(ax, x, 2.35, 2.9, .5, t, c, fs=10.5)
        ax.add_patch(FancyBboxPatch((x, .15), 2.9, 2.0, boxstyle='round,pad=0.03', fc='white', ec=c, lw=1.2))
        for i, ln in enumerate(lines):
            ax.text(x + .12, 1.85 - i * .42, ln, fontsize=9, color='#1b2033' if ln.startswith('예') else c)
        ax.text(x + 1.45, .3, f'예시 {sum(l.startswith("예") for l in lines)}개', ha='center', fontsize=9, color=GRAY)
    save(fig, 'shots')


# RAG: 검색 → 끼워 넣기 → 답변
def rag():
    fig, ax = plt.subplots(figsize=(9.5, 2.6)); ax.axis('off'); ax.set_xlim(0, 10.4); ax.set_ylim(0, 2.6)
    steps = [('① 질문', '"환불 기간은?"', GRAY), ('② 검색', '회사 문서에서\n관련 글 찾기', BLUE), ('③ 끼워 넣기', '질문 + 찾은 글\n→ 프롬프트', BLUE),
             ('④ AI 답변', '문서에 근거한\n정확한 답', GREEN)]
    for k, (t, s, c) in enumerate(steps):
        x = .1 + k * 2.6
        _box(ax, x, 1.5, 2.2, .6, t, c, fs=10.5)
        ax.text(x + 1.1, .95, s, ha='center', va='center', fontsize=9)
        if k < 3: _arrow(ax, (x + 2.25, 1.8), (x + 2.55, 1.8))
    ax.text(5.2, .15, 'RAG = Retrieval(검색) + Augmented(보강) + Generation(생성): 모르는 내용을 지어내는 환각을 줄인다', ha='center', fontsize=9, color=ORANGE)
    save(fig, 'rag')


# 컨텍스트 윈도우: 한 번에 볼 수 있는 토큰 칸
def context_window():
    fig, ax = plt.subplots(figsize=(9, 2.1)); ax.axis('off'); ax.set_xlim(0, 10); ax.set_ylim(0, 2.1)
    parts = [('시스템 프롬프트', 1.6, ORANGE), ('이전 대화', 2.6, GRAY), ('참고 문서(RAG)', 2.4, BLUE), ('이번 질문', 1.2, GREEN), ('답변 공간', 1.8, '#9db8ee')]
    x = .1
    for t, w, c in parts:
        _box(ax, x, .8, w - .08, .7, t, c, fs=9); x += w
    ax.annotate('', (9.7, .45), (.1, .45), arrowprops=dict(arrowstyle='<->', color=RED, lw=1.6))
    ax.text(4.9, .1, '컨텍스트 윈도우: 이 칸(최대 토큰 수)을 넘으면 앞부분부터 잊거나 잘린다', ha='center', fontsize=9.3, color=RED)
    save(fig, 'context_window')


if __name__ == '__main__':
    for f in [mean_median_mode, variance, quartile_box, correlation, skewness, kurtosis, scaling, histogram, normal_dist, scatter, heatmap,
              fitting, split, confusion, roc, regression, kmeans, elbow, axis, cohort, funnel, ab_test, flow, clf_reg,
              ml_map, sup_boundary, unsup_compare,
              pretrain_finetune, tokenize, embedding, entropy, learning_rate, optimizers, epoch_batch, epoch_curve,
              propagation, temperature, shots, rag, context_window]:
        f()

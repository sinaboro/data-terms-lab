# 데이터 분석 용어 랩 — 학습 교안 + 학습 앱

데이터 분석을 처음 공부하는 사람이 **용어 때문에 막히지 않도록** 만든 **용어 학습 교안(PDF)**과, 같은 내용을 폰에서 공부하는 **학습 앱**입니다.
용어마다 **한 줄 뜻 → 쉬운 설명·비유 → 그림 → 실행 예제** 순서로 풀었어요.

| 자료 | 위치 |
|---|---|
| 📄 학습 교안 (PDF, 75쪽) | [데이터분석_용어_학습교안.pdf](데이터분석_용어_학습교안.pdf) |
| 📱 학습 앱 | **https://sinaboro.github.io/data-terms-lab/** |

## 목차 (용어 105개 · 그림 24개 · 예제 86개 · 퀴즈 56문제)

| 장 | 다루는 용어 |
|---|---|
| 01 데이터 분석 기초 용어 | 데이터셋, 피처, 타깃, 관측치, 변수, 범주형·수치형 데이터, 결측치, 이상치, 중복 데이터 |
| 02 기초 통계 용어 | 평균, 중앙값, 최빈값, 분산, 표준편차, 최솟값·최댓값, 사분위수, 백분위수, 상관계수, 왜도, 첨도, 정규분포 |
| 03 데이터 전처리 용어 | 전처리, 정규화, 표준화, 인코딩, 원-핫·레이블 인코딩, 병합, 그룹화, 집계, 피처 엔지니어링, 데이터 누수 |
| 04 탐색적 데이터 분석(EDA) 용어 | EDA, 분포, 히스토그램, 산점도, 박스플롯, 히트맵, 상관분석, 교차표 |
| 05 머신러닝 기초 용어 | 지도·비지도학습, 분류, 회귀, 군집화, 차원 축소, 훈련·검증·테스트 데이터, 과적합, 과소적합, 하이퍼파라미터 |
| 06 모델 평가 용어 | 혼동행렬, Accuracy, Precision, Recall, F1-score, ROC-AUC, MAE, MSE, RMSE, R² |
| 07 비즈니스·KPI 용어 | KPI, 전환율, 유지율, 이탈률, ARPU, LTV, CAC, AOV, 코호트 분석, A/B 테스트 |
| 08 데이터 분석 전체 흐름 | 수집 → 전처리 → EDA → 피처 엔지니어링 → 모델 학습 → 평가·해석 (작은 예제로 처음부터 끝까지) |
| 09 파이썬·pandas 용어 | dtype, Series, DataFrame, axis, inplace, delimiter, describe, numeric_only, query, agg, statistic, matplotlib, scatter, prompt |
| 10 통계 모델·분석 분야 용어 | Regression(이름의 유래), LinearRegression, Intercept, Coefficient, statsmodels, OLS, Shapiro-Wilk, KMeans, Elbow, 패널 데이터, 금융 데이터, 계량 분석, 표준화 vs 정규화 |

교안 맨 뒤에 **퀴즈 정답과 해설**, 가나다순 **용어 찾아보기**가 있어요.

## 📱 학습 앱

- **학습**: 교안과 같은 내용. 그림을 누르면 크게 보여요.
- **🔍 용어 찾기**: 한글·영어로 검색 (예: `평균`, `recall`, `axis`). 누르면 설명으로 바로 가요.
- **🃏 카드 퀴즈**: 뜻↔용어 4지선다 10문제, 플래시카드. 맞힌 용어는 '외운 용어 ✓'로 기록되고, 못 외운 용어만 골라 연습할 수 있어요.
- **▶ 예제 실행**: 코드 상자를 고쳐서 바로 실행 (브라우저 안의 파이썬 Pyodide + pandas·scikit-learn·scipy·statsmodels·matplotlib). 그래프도 그림으로 나와요.
  - 처음 실행할 때만 내려받아요(pandas 약 15MB, scikit-learn 등을 쓰는 예제는 30MB 정도 더). **와이파이에서** 한 번 실행해 두면 그다음부터는 인터넷 없이도 돼요.
  - 앱의 pandas 는 2.x 라서 교안(pandas 3)과 자료형 표시가 조금 다를 수 있어요 (`str` ↔ `object`).
- 장마다 총정리 퀴즈, 진도 기록. 진도는 그 폰의 그 브라우저에만 저장돼요.

### 설치 방법 (가장 쉬운 방법: 카카오톡)
1. 카카오톡으로 받은 링크 `https://sinaboro.github.io/data-terms-lab/` 를 누릅니다.
2. 앱이 **자동으로 Chrome(아이폰은 Safari)으로 넘어갑니다.** 안 넘어가면 위쪽 안내의 **[Chrome으로 열기]** 를 누릅니다.
3. 화면 위쪽 **"홈 화면에 앱으로 설치하면…"** 안내의 **[설치]** → 확인 창에서 **설치**.
   - 안내가 안 보이면 오른쪽 아래 **📲 설치** 버튼, 또는 Chrome **`⋮` → 앱 설치(홈 화면에 추가)**
   - 아이폰은 Safari **공유 버튼 → 홈 화면에 추가 → 추가**
4. 홈 화면에 **데이터용어** 아이콘이 생깁니다.

새 용어가 추가되면 인터넷이 될 때 앱을 열면 **자동으로 업데이트**됩니다. 진도 기록은 그대로 남아요.

## 🛠 내용을 고치거나 추가하려면

원고는 `guide/chNN.md` **한 곳**에만 있고, 교안 PDF와 앱은 모두 여기서 자동으로 만들어집니다.

```
pip install reportlab pillow pandas scikit-learn scipy statsmodels matplotlib pymupdf
python tools/make_figs.py          # 설명 그림 24개 (guide/figs/)
python tools/build_pdf.py          # 교안 PDF (예제를 실제로 실행해 결과를 넣음)
python tools/build_app.py --bump   # 앱 내용 docs/content.js + 그림 복사 + 앱 버전 올리기
```

| 파일·폴더 | 설명 |
|---|---|
| `guide/ch01.md` ~ `ch10.md` | 원고. 문법은 `tools/guide_lib.py` 맨 위 설명 참고 |
| `guide/figs/` | 설명 그림 (`tools/make_figs.py` 가 matplotlib 으로 만듦) |
| `tools/guide_lib.py` | 원고 읽기 + 예제 실행 (공통, 같은 장의 예제는 이어서 실행) |
| `tools/build_pdf.py` | 교안 PDF 만들기 (ReportLab, 맑은 고딕 + D2Coding) |
| `tools/build_app.py` | 앱 데이터 만들기 |
| `tools/make_icons.py` | 앱 아이콘 |
| `docs/` | 앱 (GitHub Pages로 배포). `index.html` 화면, `app.js` 기능, `content.js` 자동 생성 내용, `sw.js` 오프라인 |

- 용어 추가 예:
  ```
  ## 02.13 | 용어 이름 · English
  @term English | 한 줄 뜻
  쉬운 설명 …
  ![그림 설명](figs/파일.png)
  ```
- 앱의 진도는 `"장/절번호"`, 외운 용어는 `"k/절번호"`로 저장되므로 용어를 추가해도 기존 기록이 유지됩니다.

강사 김대철

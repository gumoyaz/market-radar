# Market Radar

한국 주식 단기 트레이딩을 위한 **시장 분위기 분석 + 종목 선별** 도구다.

## 한 줄 정의

이 앱은 두 가지를 동시에 한다.

1. **지금 시장이 어떤 매매 전략을 허용하는지** 실시간으로 판정한다.
2. 그 시장 상태에서 **실제로 진입할 만한 종목**을 추려준다.

즉, "오늘 돌파장인가?"라는 질문과 "그러면 어떤 종목을 봐야 하는가?"라는 질문에 같이 답하는 것이 목표다.

## 2단계 파이프라인 구조

이 프로젝트의 핵심 설계는 분석을 두 단계로 나누는 것이다. 두 단계는 독립적이지 않고, **1단계의 결과가 2단계의 판정 기준을 바꾼다.**

```
[1단계] 시장 상태 판정 (Market Regime)
    질문: 지금 시장이 이 전략을 허용하는가?
    출력: 우호장 / 중립장 / 함정장 (전략별로)

           │
           │ regime이 2단계의 임계값과 컷오프를 결정한다
           ▼

[2단계] 종목 스코어링 (Candidate Selection)
    질문: 그 시장 안에서 어떤 종목이 진짜 진입 가능한가?
    출력: actionable / stalk / watch / too_extended / avoid
```

핵심 원칙:

- 함정장에서는 2단계 컷오프가 올라가서 actionable이 거의 나오지 않아야 한다
- 우호장에서는 컷오프가 내려가서 더 적극적으로 종목이 추려져야 한다
- 즉 같은 점수의 종목이라도 시장 상태에 따라 다른 결론이 나온다

## 현재 페이즈 (Phase 1) — 돌파매매

현재는 위 2단계 구조를 **돌파매매 하나로 먼저 끝까지** 만든다.

1단계 (돌파 시장 판정):

- 최근 1주일 돌파 성공률
- 최근 1~3일 돌파 유지율
- 시간대별 돌파 성과
- 첫 돌파 vs 재돌파 우세도
- 출력: `돌파 우호장 / 중립 / 함정장`

2단계 (돌파 종목 스코어링):

- 미모사식 1차 프레임 (테마/일봉/분봉/뉴스 = 테일분뉴)
- 2차 실행 프레임 (Breakout Stage / Liquidity / Leadership / Market Fit / News-Timing)
- 출력: `actionable / stalk / watch / too_extended / avoid`

## 다음 페이즈 — 다전략 확장

같은 2단계 구조를 다른 매매법으로 복제한다. 1단계 시장 판정과 2단계 종목 선별을 전략별로 따로 운영한다.

확장 전략:

- 눌림목
- 상따
- 종베
- 스윙

각 전략마다 별도의 시장 상태 판정이 붙는다. 예를 들어:

- 눌림목 우호장 / 함정장
- 상따 우호장 / 함정장
- 종베 우호장 / 함정장

같은 날 시장이 "돌파에는 함정장이지만 눌림목에는 우호장"일 수 있다. 그래서 전략별 regime을 분리한다.

최종 형태:

- 사용자가 오늘 어떤 전략이 살아있는 장인지 한눈에 본다
- 각 전략에서 추천 종목을 본다
- 전략 간 비교로 오늘의 우세 전략을 고른다

## 현재 상태

1차 프로토타입 단계다.

구현되어 있는 것:

- CSV → 정규화 → SQLite → 분석 파이프라인
- HTML / JSON 대시보드 출력
- 키움 OpenAPI+ 연동용 수집기 뼈대
- 키움 로그인 / 실시간 등록 테스트 코드
- 돌파 2단계 스코어링 로직 초안 (2단계 부분이 먼저 만들어진 상태)

진행 중 / 미완성:

- **1단계 시장 판정 로직 본격 구현** (지금은 워치리스트 평균에 의존, 진짜 시장 통계 아님)
- **돌파 이벤트 라벨링과 백테스트 모듈** (1단계의 입력이 되는 핵심 결손)
- 1단계 결과가 2단계 임계값을 바꾸는 결합 로직 (현재는 가산점 정도로만 연결)
- 장중 실시간 틱 수신 최종 검증
- 돌파매매 인터페이스 설명력 강화
- 다음 전략(눌림/상따/종베/스윙) 확장 기반 마련

## 장기 방향

`실시간 종목 추천기`가 아니라 `실시간 시장 분위기 분석기 + 그 결과로 종목 선별`이다.

장기적으로 다루고 싶은 출력:

- 오늘 살아 있는 전략은 무엇인가
- 각 전략에서 추천할 만한 종목은 무엇인가
- 시간대/주도주/수급/거래대금 측면에서 오늘 시장이 어떻게 움직이고 있는가
- 어떤 전략 조합이 최근 며칠간 잘 먹히고 있는가

## 문서

핵심 문서:

- README.md
- docs/PROJECT_SCOPE.md
- docs/TRADING_LOGIC.md
- docs/ROADMAP.md
- docs/BREAKOUT_LOGIC_V2.md
- docs/TEILBUNNYU_SCORECARD.md
- docs/LEADER_SELECTION_LOGIC.md

보조 문서:

- KIWOOM_ONBOARDING.md
- REAL_DATA_ONBOARDING.md

## 폴더 구조

```text
market-radar/
  app/                  핵심 분석 로직
  config/               런타임/수집기 설정
  data/                 샘플/템플릿/매핑 파일
  docs/                 프로젝트 범위/전략 문서
  collect_kiwoom_raw.py 키움 raw 수집기 진입점
  dashboard.py          HTML 대시보드 생성
  main.py               메인 분석 실행기
  monitor.py            반복 갱신형 실행기
  run_pipeline.py       원본 CSV → 분석 파이프라인 일괄 실행
```

## 빠른 실행

샘플 메모리 데이터 분석:

```powershell
python main.py
```

샘플 HTML 대시보드 생성:

```powershell
python dashboard.py
```

원본 CSV → 정규화 → DB → 리포트 → 대시보드:

```powershell
python run_pipeline.py --raw-dir data/raw_sample --mapping data/mappings/example_mapping.json --workspace pipeline_output
```

키움 로그인 테스트:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_login_test_32.ps1
```

키움 실시간 등록 테스트:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_realtime_test_32.ps1
```

## 다음 우선순위

현재 시점 기준 작업 순서:

1. **1단계 시장 판정 로직 정식 구현**
   - 돌파 이벤트 자동 라벨링 (진입 후 +2% 도달 / -1% 이탈 기준)
   - 최근 N일 돌파 성공률, 시간대별 성공률, 재돌파 우세도 자동 산출
   - 워치리스트가 아닌 시장 전체 기준 통계
2. **1단계 → 2단계 결합 강화**
   - regime이 2단계의 actionable 컷오프와 가중치를 직접 바꾸도록 수정
   - 현재의 가산/감점 방식은 약함
3. 장중 실시간 수집 검증 마무리
4. 돌파 2단계 스코어링 인터페이스 설명력 강화
5. 다음 전략(눌림/상따/종베/스윙) 확장을 위한 1단계/2단계 인터페이스 추상화

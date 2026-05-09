# Market Radar

한국 주식 단기 트레이딩을 위한 시장 분위기 분석 프로젝트다.

이 프로젝트의 목표는 단순히 "지금 살 종목"을 뽑는 것이 아니라, 최근 시장이 어떤 전략을 허용하는지 정량적으로 파악하는 것이다.

예를 들어 아래 질문에 답하는 것을 목표로 한다.

- 최근 1주일 돌파매매 성공률은 어떤가
- 최근 시장은 돌파 친화장인가, 함정장인가
- 어떤 시간대에 돌파가 잘 되는가
- 거래대금, 프로그램 매수, 주도주 여부가 성과에 어떤 영향을 주는가

## 현재 방향

현재 페이즈의 중심은 `돌파매매`다.

지금 하고 있는 일:

- 돌파매매를 위한 로직 설계
- 돌파매매를 위한 인터페이스 설계
- 최근 돌파 트렌드와 시장 분위기 해석

다음 페이즈에서 확장할 전략:

- 눌림목
- 종베
- 상따
- 스윙

즉, 지금은 범위를 넓게 벌리기보다 `돌파매매 하나를 제대로 정의하고 보여주는 것`이 우선이다.

## 현재 상태

현재는 1차 프로토타입 단계다.

구현되어 있는 것:

- CSV -> 정규화 -> SQLite -> 분석 파이프라인
- HTML / JSON 대시보드 출력
- 키움 OpenAPI+ 연동용 수집기 뼈대
- 키움 로그인 테스트 및 실시간 등록 테스트 코드
- 돌파 중심 점수화/시장 상태 분석 로직 초안

아직 진행 중인 것:

- 장중 실시간 틱 수신 최종 검증
- 돌파매매 인터페이스 설명력 강화
- 돌파 트렌드/시장 상태 대시보드 재구성
- 전략 정의 고도화와 백테스트 체계화

## 장기 방향

초기에는 브레이크아웃 분석기로 시작했지만, 장기적으로는 더 넓은 시장 분위기 분석기로 간다.

장기적으로 다루고 싶은 범위:

- 돌파매매 분석
- 눌림목 분석
- 상따매매 분석
- 종베매매 분석
- 스윙 분석
- 시간대별 전략 성과 분석
- 시장 레짐 분류
- 주도주/수급/거래대금 기반 시장 분위기 해석

즉, 최종적으로는 `실시간 종목 추천기`보다 `실시간 시장 분위기 분석기`에 가깝다.

## 문서

핵심 문서:

- [README.md](C:/Users/Vince-PC/Documents/Codex/market-radar/README.md)
- [docs/PROJECT_SCOPE.md](C:/Users/Vince-PC/Documents/Codex/market-radar/docs/PROJECT_SCOPE.md)
- [docs/TRADING_LOGIC.md](C:/Users/Vince-PC/Documents/Codex/market-radar/docs/TRADING_LOGIC.md)
- [docs/ROADMAP.md](C:/Users/Vince-PC/Documents/Codex/market-radar/docs/ROADMAP.md)

보조 문서:

- [KIWOOM_ONBOARDING.md](C:/Users/Vince-PC/Documents/Codex/market-radar/KIWOOM_ONBOARDING.md)
- [REAL_DATA_ONBOARDING.md](C:/Users/Vince-PC/Documents/Codex/market-radar/REAL_DATA_ONBOARDING.md)

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
  run_pipeline.py       원본 CSV -> 분석 파이프라인 일괄 실행
```

## 빠른 실행

샘플 메모리 데이터 분석:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" main.py
```

샘플 HTML 대시보드 생성:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" dashboard.py
```

원본 CSV -> 정규화 -> DB -> 리포트 -> 대시보드:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" run_pipeline.py --raw-dir data/raw_sample --mapping data/mappings/example_mapping.json --workspace pipeline_output
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

1. 돌파매매 로직 정리
2. 돌파매매 인터페이스 설계
3. 최근 돌파 트렌드/시장 상태 대시보드 강화
4. 장중 실시간 수집 검증 마무리
5. 다음 페이즈 전략 확장 준비

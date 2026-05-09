# Breakout Analyzer Skeleton

브레이크아웃 시장 분석기 1차 버전이다. 외부 라이브러리 없이 돌아가고, 이제 `CSV -> SQLite -> 분석` 흐름까지 포함한다.

## 포함된 로직

- 소형주 `분당 거래대금 30억 이상`
- 중형 이상 `분당 거래대금 60억 이상`
- 최근 3분 지속 여부
- `52주 신고가`, `당일 고가`, `전일 고가`, `재돌파`, `VI 직전 압축` 패턴 탐지
- 시간대 적합도 반영
- 시장 상태 `favorable / neutral / trap` 계산
- 종목 점수화

## 실행 예시

샘플 메모리 데이터 바로 실행:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" main.py
```

샘플 HTML 대시보드 생성:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" dashboard.py
```

CSV를 주기적으로 다시 읽어서 라이브 대시보드/JSON 갱신:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" monitor.py --import-csv-dir data/sample_csv --interval-sec 60 --cycles 0
```

원본 CSV 컬럼명을 표준 포맷으로 변환:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" normalize_csv.py --raw-dir data/raw_sample --mapping data/mappings/example_mapping.json --output-dir data/normalized_from_raw
```

원본 CSV 헤더를 보고 시작용 매핑 파일 자동 생성:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" inspect_csv_headers.py --raw-dir data/raw_sample --output-report output/csv-header-report.md --output-mapping output/starter-mapping.json
```

원본 CSV에서 리포트/정규화/DB/대시보드까지 한 번에 실행:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" run_pipeline.py --raw-dir data/raw_sample --mapping data/mappings/example_mapping.json --workspace pipeline_output
```

키움 기준 설정으로 파이프라인 실행:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" kiwoom_run.py
```

키움 raw CSV 수집기 실행:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" collect_kiwoom_raw.py
```

키움 live 모드는 `PyQt5.QAxContainer`와 키움 OpenAPI+ 설치가 필요하다.

설치 후 환경 점검:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" check_kiwoom_env.py
```

32비트 Python 기반 키움 로그인 테스트:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_login_test_32.ps1
```

32비트 Python 기반 키움 live 수집:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_live_32.ps1
```

32비트 Python 기반 실시간 이벤트 단건 테스트:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_realtime_test_32.ps1
```

샘플 데이터를 SQLite에 넣고 DB 기준으로 실행:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" main.py --source db --seed-sample-db
```

CSV 디렉터리를 SQLite로 적재 후 실행:

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" main.py --source db --import-csv-dir data/sample_csv
```

## CSV 포맷

`symbol_profiles.csv`

```text
symbol,name,size_group,day_high,prev_day_high,high_52w,vi_price,is_leader_stock
```

`minute_bars.csv`

```text
symbol,ts,close,turnover_billion,program_net_buy_billion
```

`time_bucket_stats.csv`

```text
symbol,bucket,pattern,success_rate,trap_rate
```

## 원본 CSV 변환

실제 증권사/수집기 CSV는 컬럼명이 다를 수 있으니, 먼저 `normalize_csv.py`로 표준 포맷으로 맞춘 다음 `main.py`, `dashboard.py`, `monitor.py`에 넣으면 돼.

- 원본 예시: [data/raw_sample](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/raw_sample)
- 매핑 예시: [data/mappings/example_mapping.json](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/mappings/example_mapping.json)
- 변환 출력: `data/normalized_from_raw`
- 헤더 점검 리포트: `output/csv-header-report.md`
- 자동 생성 시작용 매핑: `output/starter-mapping.json`

## 출력 파일

- 콘솔 분석: 터미널에 바로 출력
- HTML 대시보드: `output/dashboard.html`
- 라이브 HTML 대시보드: `output/live-dashboard.html`
- 라이브 JSON 스냅샷: `output/live-dashboard.json`
- 통합 파이프라인 출력: `pipeline_output/`

## 다음 단계

1. 실제 증권사/API 데이터 연결
2. 장중 반복 적재 작업 추가
3. 장마감 라벨링과 백테스트 구현
4. Streamlit 또는 React 대시보드 연결
5. 이후 재학습 파이프라인 추가

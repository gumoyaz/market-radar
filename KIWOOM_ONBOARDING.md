# Kiwoom Onboarding

키움 Open API+ 기준으로 이 프로젝트를 붙일 때의 실전 메모다.

## 전제

- 실제 매매는 키움에서 한다.
- 분석 결과도 가능하면 키움 데이터 기준으로 맞춘다.
- 현재 프로젝트는 `CSV -> 표준화 -> DB -> 분석/대시보드` 구조다.

즉, 키움 연동의 핵심은 먼저 **키움 데이터가 떨어지는 raw CSV 폴더를 만드는 것**이다.

## 권장 구조

1. 키움 Open API+ 또는 HTS/보조수집기로 raw CSV 생성
2. 이 프로젝트가 raw CSV를 표준 포맷으로 변환
3. SQLite 적재
4. 돌파/재돌파/시간대/시장상태 분석
5. 필요하면 나중에 키움 주문 연동

## 왜 이 방식이 좋은가

- 주문 증권사와 데이터 기준을 맞출 수 있다.
- 수집기와 분석기를 분리해서 디버깅이 쉽다.
- 키움 수집부가 바뀌어도 분석 엔진은 거의 안 바뀐다.

## raw CSV 최소 3종

### 1. 종목 기본정보

- 파일 예시: `raw_symbol_profiles.csv`
- 필수 정보:
  - 종목코드
  - 종목명
  - 시총구분
  - 당일고가
  - 전일고가
  - 52주고가
  - VI가격
  - 주도주여부

### 2. 분봉 또는 체결 기반 최근 데이터

- 파일 예시: `raw_minute_bars.csv`
- 필수 정보:
  - 종목코드
  - 체결시각
  - 현재가
  - 분당거래대금
  - 프로그램순매수

### 3. 시간대/패턴 통계

- 파일 예시: `raw_time_bucket_stats.csv`
- 필수 정보:
  - 종목코드
  - 시간대
  - 패턴
  - 성공률
  - 함정비율

## 시작 방법

### 1. 키움용 설정 파일 수정

- [config/kiwoom_runtime.json](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/config/kiwoom_runtime.json)
- [config/kiwoom_collector.json](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/config/kiwoom_collector.json)

여기서 바꿀 것:

- `raw_dir`: 키움 raw CSV가 떨어지는 폴더
- `mapping_path`: 키움 raw 헤더와 표준 필드를 연결하는 매핑 JSON
- `time_bucket`: 현재 분석 기준 시간대
- `watchlist_path`: mock 수집 기준 종목 목록

### 2. raw 폴더 준비

템플릿은 여기:

- [data/kiwoom_raw_template/raw_symbol_profiles.csv](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/kiwoom_raw_template/raw_symbol_profiles.csv)
- [data/kiwoom_raw_template/raw_minute_bars.csv](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/kiwoom_raw_template/raw_minute_bars.csv)
- [data/kiwoom_raw_template/raw_time_bucket_stats.csv](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/kiwoom_raw_template/raw_time_bucket_stats.csv)
- mock 수집 시드: [data/kiwoom_seed/watchlist.json](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/kiwoom_seed/watchlist.json)

### 3. 헤더가 다르면 먼저 점검

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" inspect_csv_headers.py --raw-dir data/kiwoom_raw_template --output-report output/kiwoom-header-report.md --output-mapping output/kiwoom-starter-mapping.json
```

### 4. 키움 전용 파이프라인 실행

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" kiwoom_run.py
```

### 5. 키움 raw CSV 수집기 실행

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" collect_kiwoom_raw.py
```

현재 수집기는 `mock` 모드라서 키움 실연결 대신 raw CSV를 자동 생성한다.
나중에는 이 수집기 내부의 mock provider를 키움 OpenAPI+ 로그인/실시간 수신 코드로 교체하면 된다.

## live 모드 전제조건

`config/kiwoom_collector.json`에서 `mode`를 `live`로 바꾸려면 아래가 필요하다.

- Windows 환경
- 키움 OpenAPI+ 설치
- 키움 OpenAPI+ 사용등록 완료
- PyQt5 + QAxContainer 사용 가능한 파이썬 환경

현재 이 작업 폴더에는 live 어댑터 코드가 들어 있지만, 번들 파이썬에는 `PyQt5.QAxContainer`가 없어서 여기서 직접 실접속 검증은 못 했다.
실제 사용자 PC에서 해당 환경이 준비되면 `collect_kiwoom_raw.py`의 live 모드로 연결할 수 있다.

## 현재 이 PC에서 확인된 상태

- `C:\OpenAPI` 설치 경로 확인됨
- 32비트 Python 3.11.9 설치됨
- 32비트 Python에서 `PyQt5.QAxContainer` 확인됨
- 32비트 Python에서 `KHOPENAPI.KHOpenAPICtrl.1` ActiveX 로딩 확인됨

즉, 지금은 **로그인 테스트와 live 수집을 시도할 수 있는 상태**다.

## 바로 실행할 명령

로그인 테스트:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_login_test_32.ps1
```

live 수집:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_live_32.ps1
```

실시간 이벤트 단건 디버그:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_kiwoom_realtime_test_32.ps1
```

## 나중에 붙일 실연결 수집기

실수집기는 보통 별도 프로세스로 만드는 걸 권장한다.

- `kiwoom_collector.exe` 또는 파이썬 수집기
- 역할:
  - 로그인
  - 관심종목/조건검색 로딩
  - 분봉/체결/거래대금/프로그램/VI 관련 데이터 수집
  - raw CSV 또는 SQLite로 기록

현재 프로젝트는 그 수집기의 출력만 받으면 된다.

## 현실적인 개발 순서

1. 키움 raw CSV 구조 확정
2. 매핑 JSON 작성
3. 키움 수집기에서 raw CSV 배출
4. 이 프로젝트로 분석 자동화
5. 분석이 맞는지 충분히 검증
6. 마지막에만 주문 연동

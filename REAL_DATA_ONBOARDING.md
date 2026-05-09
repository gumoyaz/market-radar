# Real Data Onboarding

실제 CSV가 아직 없을 때도, 나중에 바로 붙일 수 있게 준비하는 문서다.

## 1. 원본 CSV 준비

아래 3개 파일이 있으면 현재 파이프라인에 바로 연결할 수 있다.

- `raw_symbol_profiles.csv`
- `raw_minute_bars.csv`
- `raw_time_bucket_stats.csv`

파일명은 달라도 되지만, 그 경우 매핑 JSON의 `source` 값만 바꾸면 된다.

## 2. 최소 컬럼

### raw_symbol_profiles.csv

```text
symbol,name,size_group,day_high,prev_day_high,high_52w,vi_price,is_leader_stock
```

### raw_minute_bars.csv

```text
symbol,ts,close,turnover_billion,program_net_buy_billion
```

### raw_time_bucket_stats.csv

```text
symbol,bucket,pattern,success_rate,trap_rate
```

## 3. 값 규칙

- `size_group`: `small`, `mid`, `large`
- `is_leader_stock`: `true` 또는 `false`
- `pattern`: `high_52w`, `day_high`, `prev_day_high`, `rebreak`, `pre_vi`
- `turnover_billion`: 억 단위 기준 숫자
- `program_net_buy_billion`: 억 단위 기준 숫자
- `ts`: 예시 `2026-04-23T09:10:00`

## 4. 실제 헤더명이 다를 때

원본 파일 헤더가 다르면 먼저 아래 명령으로 헤더 리포트를 만든다.

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" inspect_csv_headers.py --raw-dir 네원본폴더 --output-report output/csv-header-report.md --output-mapping output/starter-mapping.json
```

그다음 `starter-mapping.json`을 네 헤더명에 맞게 수정하고, 아래 파이프라인을 돌리면 된다.

```powershell
& "C:\Users\Vince-PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" run_pipeline.py --raw-dir 네원본폴더 --mapping 네매핑파일.json --workspace pipeline_output
```

## 5. 가장 쉬운 시작 방법

실제 데이터가 생기기 전까지는 아래 폴더의 템플릿 파일에 맞춰 CSV를 만들어두면 된다.

- [data/raw_template/raw_symbol_profiles.csv](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/raw_template/raw_symbol_profiles.csv)
- [data/raw_template/raw_minute_bars.csv](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/raw_template/raw_minute_bars.csv)
- [data/raw_template/raw_time_bucket_stats.csv](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/raw_template/raw_time_bucket_stats.csv)
- [data/mappings/raw_template_mapping.json](C:/Users/Vince-PC/Documents/Codex/2026-04-23-new-chat/data/mappings/raw_template_mapping.json)

# Leader Selection Logic

## 본 문서의 위치
이 문서는 본 프로젝트의 2단계(Candidate Scoring) 내부의 리더 선정 로직을 정의한다.
본 프로젝트의 1단계(Market Regime Judgment)는 별도이며, 1단계 결과가
2단계 전반의 컷오프와 가중치를 바꾼다. 자세한 구조는 PROJECT_SCOPE.md 참조.

## 목적

이 문서는 `테일분뉴 프레임 선별`을 통과한 종목들 가운데,
같은 테마 안에서 어떤 종목을 `주도주 / 대장주`로 볼지,
그리고 실제 매수 대상을 `상승률 1등`으로 볼지 `거래대금 1등`으로 볼지 정리한 문서다.

핵심은 두 가지다.

1. `대장주 정의`
2. `가격 리더 vs 자금 리더 선택`

---

## 기본 개념

### 1. 가격 리더

- 같은 테마 안에서 가장 빨리, 가장 크게 올라가는 종목
- 당일 상승률 1등이거나 전고 돌파 속도가 가장 빠른 종목
- `return leader`

### 2. 자금 리더

- 같은 테마 안에서 거래대금이 가장 많이 들어오는 종목
- 분봉 기준 돈이 가장 오래, 가장 두껍게 붙는 종목
- `turnover leader`

### 3. 듀얼 리더

- 상승률도 상위권이고 거래대금도 상위권인 종목
- 속도와 자금이 같이 붙는 가장 이상적인 리더
- `dual leader`

---

## 왜 둘을 나눠야 하나

단순히 많이 오른 종목만 따라가면 `가격만 튄 종목`을 추격하게 될 수 있다.
반대로 거래대금만 많다고 무조건 좋은 것도 아니다.
돈은 몰리지만 가격은 덜 가는 `무거운 종목`일 수도 있다.

그래서 실행 프레임에서는 아래를 같이 본다.

- 누가 가장 많이 오르는가
- 누가 가장 많은 돈을 먹는가
- 그 차이가 얼마나 큰가
- 그 상태가 몇 분 동안 유지되는가
- 뉴스와 테마가 어느 종목을 중심으로 모이는가

---

## 자료에서 가져온 기준

### 학술 자료에서 가져온 점

1. `업종/테마 흐름 자체가 중요하다`
- Moskowitz and Grinblatt (1999)는 개별 종목 모멘텀의 상당 부분이 산업/업종 모멘텀으로 설명된다고 본다.
- 즉 종목보다 먼저 `테마 안에서 누가 리더인지`를 보는 것이 맞다.

2. `한국 시장에서 가격만 쫓는 전통적 모멘텀은 뒤집힐 수 있다`
- Sim et al. (2022), Kang et al. (2025) 자료상 한국 시장에서는 전통적 개별 종목 모멘텀이 약하거나 reversal 성격이 강하다.
- 즉 `상승률 1등`만 쫓는 로직은 그대로 쓰기 위험하다.

3. `비정상 거래대금은 짧은 구간에서 예측력이 있다`
- Lee, Kim, and Kim (2016), Li, Yin, and Zhao (2024)는 abnormal trading volume이 짧은 구간에서 후속 수익률과 연결될 수 있음을 보여준다.
- 따라서 `거래대금 1등`은 중요한 축이다.

4. `다만 큰 가격 급등 + 큰 거래량은 추격 구간에 따라 과열일 수도 있다`
- Kudryavtsev (2019)는 큰 가격 변화와 높은 비정상 거래량이 붙은 경우 이후 reversal 가능성도 있음을 보여준다.
- 그래서 `돈이 가장 많이 들어왔다`는 이유만으로 후행 추격하면 안 되고,
  그 돈이 `돌파 초입`에 붙는지 `이미 멀어진 뒤` 붙는지를 나눠야 한다.

### 실전 트레이더 관점에서 가져온 점

공개 블로그/실전 글들에서는 공통적으로:

- `상승률 1등`
- `거래대금 1등`
- `뉴스가 몰리는 종목`
- `테마 내 선발주`

를 같이 보라고 한다.

즉 실전적으로도 `가격 리더`와 `자금 리더`를 둘 다 보는 게 일반적이다.

---

## 대장주 정의

현재 프로젝트에서는 아래 5개를 합쳐 대장주를 정의한다.

1. `테마 내 거래대금 순위`
- 1위 또는 2위인가

2. `테마 내 상승률 순위`
- 1위 또는 2위인가

3. `거래대금 점유율`
- 같은 테마 전체 거래대금 중 이 종목이 얼마나 먹는가

4. `상승 지속 시간`
- 몇 분 동안 선두를 유지하는가

5. `뉴스 중심성`
- 뉴스가 이 종목을 직접 때리는가
- 아니면 테마만 강하고 이 종목 자체는 후발인가

즉 대장주는
`많이 오른 종목` 하나로 정의하지 않고,
`돈 + 속도 + 지속성 + 뉴스 중심성`으로 정의한다.

---

## 리더 선택 규칙

### 1. buy_dual_leader

아래면 최우선이다.

- 거래대금 1위
- 상승률 1~2위
- 거래대금 점유율 높음
- 뉴스/테마 정렬
- 돌파 stage가 `breaking` 또는 `holding`

해석:
- 돈과 속도가 같은 종목에 붙었다
- 가장 이상적인 대장주

### 2. buy_return_leader

아래 조건이면 가격 리더를 우선 본다.

- 상승률 1위
- 거래대금도 최소 2위 안
- 뉴스가 매우 신선함
- 테마가 아직 초입
- 돌파가 막 시작되는 구간

해석:
- 새 뉴스와 첫 가속 구간에서는 `제일 빨리 치는 종목`이 대장일 가능성이 높다
- 다만 거래대금까지 최소 상위권이어야 한다

### 3. buy_turnover_leader

아래 조건이면 자금 리더를 우선 본다.

- 거래대금 1위
- 상승률도 최소 3위 안
- 테마가 넓게 퍼졌거나
- 뉴스가 신선하지 않거나
- 이미 `holding` 이후 구간이거나
- 시장이 함정장에 가까움

해석:
- 장이 진행될수록 `제일 많이 오른 종목`보다 `제일 큰 돈이 버티는 종목`이 더 신뢰할 만하다
- 후기 구간 / 군중 추격 구간일수록 가격 리더보다 자금 리더를 우선한다

### 4. wait_for_resolution

아래면 바로 사지 않는다.

- 상승률 1등인데 거래대금 순위가 너무 낮음
- 거래대금 1등인데 가격 반응이 너무 약함
- 선두가 자주 바뀜
- 돌파 stage가 아직 `probing`

해석:
- 아직 진짜 대장이 정해지지 않은 상태
- 이때는 테마는 좋아도 종목 선택은 기다린다

---

## 실전 선택 원칙

### A. 테마 초입

아래면 `상승률 리더` 가중치를 높인다.

- 뉴스가 막 나옴
- 테마 참여 종목 수가 적음
- 첫 돌파
- 시장이 돌파 우호장

이유:
- 초기에는 속도가 대장을 만든다

### B. 테마 확산 구간

아래면 `거래대금 리더` 가중치를 높인다.

- 참여 종목 수가 늘어남
- 뉴스가 시장에 이미 퍼짐
- 재돌파/눌림 후 재상승 구간
- 장이 중립 또는 함정장

이유:
- 후기에는 속도보다 돈의 지속이 더 중요하다

### C. 과열 구간

아래면 무조건 보수적으로 본다.

- 상승률 1등인데 이미 너무 멂
- 거래대금은 터졌지만 고가 안착이 약함
- leader 교체가 잦음

이유:
- 이런 구간은 `대장주 선정`이 아니라 `추격 리스크 관리`가 우선이다

---

## 현재 코드 기준 입력값

현재 리더 로직은 아래 입력값을 받도록 설계했다.

- `theme_member_count`
- `turnover_rank`
- `return_rank`
- `turnover_share_pct`
- `intraday_return_pct`
- `gap_from_next_turnover_pct`
- `gap_from_next_return_pct`
- `move_persistence_minutes`
- `is_news_leader`

그리고 최종 출력은 아래 4개다.

- `leadership_score`
- `buy_dual_leader`
- `buy_return_leader`
- `buy_turnover_leader`
- `wait_for_resolution`

---

## 권장 인터페이스 출력

종목 카드에 아래를 보여줘야 한다.

- `theme leader rank`
- `turnover rank`
- `return rank`
- `leader choice`
- `leaderhip score`
- `buy return leader / buy turnover leader / wait`

즉 종목 카드에서
`왜 이 종목을 대장으로 봤는지`
또는
`왜 아직 대장 확정이 안 됐는지`
가 바로 보여야 한다.

---

## 참고 자료

- Moskowitz, T. J., & Grinblatt, M. (1999). Do Industries Explain Momentum?  
  https://ideas.repec.org/a/bla/jfinan/v54y1999i4p1249-1290.html
- Sim, M., Kang, J., Kim, H. E., & Lee, E. (2022). The Momentum Strategies and Salience: Evidence from the Korean Stock Market.  
  https://www.tandfonline.com/doi/full/10.1080/1540496X.2022.2034615
- Kang, D., Ryu, D., & Webb, R. I. (2025). Momentum and reversal effects in the Korean stock market.  
  https://www.tandfonline.com/doi/full/10.1080/10293523.2024.2448054
- Lee, D. H., Kim, M. K., & Kim, T. S. (2016). Abnormal Trading Volume and the Cross-Section of Stock Returns.  
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2812010
- Li, M., Yin, X., & Zhao, J. (2024). Persistence or reversal? The effects of abnormal trading volume on stock returns.  
  https://www.tandfonline.com/doi/full/10.1080/1351847X.2024.2303092
- Kudryavtsev, A. (2019). The effect of trading volumes on stock returns following large price moves.  
  https://doaj.org/article/0d7d0d06e2f648e390af2afba0811f2d

실전 관행 참고:

- https://pokmmkop.tistory.com/entry/%F0%9F%94%A5-%EC%A7%80%EA%B8%88-%EC%8B%9C%EC%9E%A5%EC%97%90%EC%84%9C-%E2%80%9C%EC%A7%84%EC%A7%9C-%EB%8C%80%EC%9E%A5%EC%A3%BC-%EC%B0%BE%EB%8A%94-%EB%B0%A9%EB%B2%95%E2%80%9D
- https://jewel-chest.tistory.com/entry/%F0%9F%A7%AD-1%EF%B8%8F%E2%83%A3-%EC%8B%9C%EC%9E%A5%EC%9D%84-%EC%9D%B4%EA%B8%B0%EB%8A%94-%EC%B2%AB-%EB%8B%A8%EA%B3%84-%E2%80%94-%E2%80%9C%EB%8C%80%EC%9E%A5%C2%B7%EC%A3%BC%EB%8F%84%EC%A3%BC-%ED%83%90%EC%A7%80-%EB%A3%A8%ED%8B%B4%E2%80%9D

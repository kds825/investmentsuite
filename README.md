# PE 투자보고서 자동 생성 MVP

투자위원회(IC) 수준의 투자보고서를 자동으로 생성하는 Streamlit 기반 애플리케이션입니다.

## 주요 기능

- **3가지 보고서 모드**: IC Memo / Full DD Report / Legal + Finance Appendix
- **6개 전문 에이전트**: DD, Consulting, Legal, FinanceCost, ExitStrategy, Orchestrator
- **애널리스트 워크플로우**: Assumption Log, Open Questions, IC-ready Summary Box, Evidence 인용
- **HTML/PDF 출력**: outputs/ 폴더 저장 + 다운로드

## 빠른 시작

```bash
# 1. 가상환경 생성
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
copy .env.example .env       # Windows
# cp .env.example .env       # Mac/Linux
# .env 파일을 편집하여 API 키 설정

# 4. 실행
streamlit run apps/web/app.py
```

## 환경변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | `sk-...` |
| `OPENAI_MODEL` | 사용할 모델 | `gpt-4` |
| `OPENAI_API_BASE_URL` | API 엔드포인트 (OpenAI-compatible) | `https://api.openai.com/v1` |

## 레포 구조

```
/apps/web/app.py                          # Streamlit 앱
/packages/core/llm_client.py              # LLM 클라이언트 (유일한 LLM 호출 지점)
/packages/agents/orchestrator.py          # 오케스트레이터
/packages/agents/dd_agent.py              # DD Agent (실사)
/packages/agents/consulting_agent.py      # Consulting Agent (전략)
/packages/agents/legal_agent.py           # Legal Agent (법무)
/packages/agents/finance_cost_agent.py    # FinanceCost Agent (재무)
/packages/agents/exit_strategy_agent.py   # ExitStrategy Agent (엑싯)
/packages/report/generator.py            # 보고서 생성기
/packages/report/templates/report.html.j2 # HTML 템플릿
/outputs/                                 # 생성된 보고서 저장
```

## 보고서 모드

### IC Memo
투자위원회용 1페이지 요약. Consulting + ExitStrategy 에이전트 동원.

### Full DD Report
전체 실사 보고서. 모든 에이전트(5개) 동원하여 13개 필수 섹션 생성.

### Legal + Finance Appendix
법무/재무 부록만 빠르게 생성.

## 애널리스트 워크플로우 설명

보고서는 단순 챗봇 출력이 아닌, 실제 투자사 업무 산출물 수준으로 설계되었습니다:

1. **Assumption Log**: 사용자 제공 정보, 미확인 정보(Unknown), 판단 기준을 분리 표기
2. **Open Questions**: 바로 실행 가능한 다음 행동 목록
3. **IC-ready Summary Box**: 결론(추천/보류/반대) + 근거 3개 + 핵심 리스크 3개 + Deal Breaker
4. **Evidence 인용**: 입력 텍스트에서 quote 형태로 근거 인용, 없으면 "자료 필요" 표기
5. **평가 등급**: Green / Yellow / Red (숫자 점수 사용 금지)

## PDF 출력

PDF는 WeasyPrint를 사용합니다.

- **Windows**: WeasyPrint는 GTK 라이브러리가 필요합니다. [설치 가이드](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)
- **Mac**: `brew install pango`
- **Linux**: `apt install libpango-1.0-0 libpangoft2-1.0-0`

WeasyPrint가 설치되지 않아도 HTML 보고서는 정상 동작합니다.

## 데모 입력 예시

### 예시 1: B2B SaaS 성장 투자
- 회사명: 클라우드솔루션즈
- 업종: B2B SaaS (ERP)
- 투자 목적: 성장 (Growth)
- 투자 기간: 5년
- 엑싯 선호: IPO
- 리스크 선호도: 중립 (Neutral)
- 보고서 모드: Full DD Report
- 메모: "연매출 200억, ARR 성장률 30%, 고객 이탈률 5% 미만, 창업자 지분 60%"

### 예시 2: 제조업 턴어라운드
- 회사명: 대한정밀공업
- 업종: 자동차 부품 제조
- 투자 목적: 턴어라운드 (Turnaround)
- 투자 기간: 3년
- 엑싯 선호: 전략적 매각 (Strategic Sale)
- 리스크 선호도: 공격적 (Aggressive)
- 보고서 모드: IC Memo
- 메모: "매출 500억, 영업이익률 -3%, 주요 고객사 현대차/기아, 공장 노후화 이슈"

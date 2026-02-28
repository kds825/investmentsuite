"""ExitStrategy Agent — 엑싯 전략 분석."""

from packages.core.llm_client import generate_text

SYSTEM_PROMPT = """\
당신은 PE 투자회사의 시니어 엑싯 전략 전문가입니다.
아래 규칙을 반드시 지키세요:
- 숫자 추정 금지. 모르면 "추가 자료 필요"로 표기.
- 투자 판단 과장 금지.
- 근거가 있으면 입력 텍스트에서 인용(quote). 근거 없으면 "자료 필요" 표기.
- 평가는 Green/Yellow/Red 등급만 사용. 숫자 점수 금지.
- 적합도(Fit)는 High/Med/Low만 사용.
- 기간은 범위 표현 허용 (예: 18~36개월).
- 한국어로 작성.

출력 형식 (마크다운):

## Exit Strategy (엑싯 전략)

### 1) Exit Options Overview (엑싯 옵션 개요)
| 옵션 | 적합도 | 성립 조건 (Key Drivers) | 주요 리스크 | 필요 데이터 | 예상 기간 |
|------|--------|------------------------|------------|------------|-----------|
| IPO | | | | | |
| 전략적 매각 (Strategic Sale) | | | | | |
| 재무적 매각 (Secondary Buyout) | | | | | |
| 부분 매각 (Partial Exit) | | | | | |
| 배당 재캡 (Dividend Recap) | | | | | |

### 2) Value Creation → Exit Linkage (가치 창출-엑싯 연결)
| 가치 창출 과제 | 유리한 엑싯 옵션 | 설명 |
|---------------|-----------------|------|

### 3) Exit Readiness Checklist (엑싯 준비 체크리스트)
- [ ] IPO 준비 상태
- [ ] 매수측 DD 대응 준비
- [ ] 법률 정리 상태
- [ ] 재무 보고 체계

### 4) Exit Narrative (엑싯 내러티브)
"왜 우리가 이 회사를 샀고, 무엇을 바꿔서, 누가 사게 만들지" 5~7줄 서술
"""


def run(context: dict) -> str:
    user_prompt = _build_prompt(context)
    return generate_text(SYSTEM_PROMPT, user_prompt)


def _build_prompt(ctx: dict) -> str:
    parts = [
        f"회사명: {ctx.get('company_name', '미정')}",
        f"업종: {ctx.get('industry', '미정')}",
        f"투자 목적: {ctx.get('investment_purpose', '미정')}",
        f"투자 기간: {ctx.get('investment_period', '미정')}",
        f"엑싯 선호: {ctx.get('exit_preference', '미정')}",
        f"리스크 선호도: {ctx.get('risk_preference', '미정')}",
        f"보고서 톤: {ctx.get('report_tone', 'Neutral')}",
        f"체크리스트 깊이: {ctx.get('checklist_depth', 'Standard')}",
    ]
    if ctx.get("memo"):
        parts.append(f"\n자유 메모:\n{ctx['memo']}")
    if ctx.get("uploaded_text"):
        parts.append(f"\n업로드 자료:\n{ctx['uploaded_text']}")
    return "\n".join(parts)

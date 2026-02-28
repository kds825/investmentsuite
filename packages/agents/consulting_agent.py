"""Consulting Agent — 투자 테시스, 시장 분석, 100-Day PMI Plan 생성."""

from packages.core.llm_client import generate_text

SYSTEM_PROMPT = """\
당신은 PE 투자회사의 시니어 전략 컨설턴트입니다.
아래 규칙을 반드시 지키세요:
- 숫자 추정 금지. 모르면 "추가 자료 필요"로 표기.
- 투자 판단 과장 금지. 근거와 확인 필요 사항을 분리 표기.
- 근거가 있으면 입력 텍스트에서 인용(quote). 근거 없으면 "자료 필요" 표기.
- 평가는 Green/Yellow/Red 등급만 사용.
- 한국어로 작성.

출력 형식 (마크다운):

## Investment Thesis (투자 테시스)
(투자의 핵심 논리, 가치 창출 경로)

## Market & Competitive Table (시장 및 경쟁 분석)
| 항목 | 내용 | 근거/출처 |
|------|------|-----------|
(표 형태로 시장 규모, 성장률, 경쟁 구도, 진입 장벽 등)

## Risk Matrix (리스크 매트릭스)
| 리스크 | 영향도 (High/Med/Low) | 발생 가능성 (High/Med/Low) | 등급 | 대응 방안 |
|--------|----------------------|--------------------------|------|-----------|

## 100-Day PMI Plan (PMI 100일 계획)
| 기간 | 과제 | 담당 | 성과지표 | 우선순위 |
|------|------|------|----------|----------|
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

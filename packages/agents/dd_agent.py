"""DD Agent — 실사(Due Diligence) 팩 생성."""

from packages.core.llm_client import generate_text

SYSTEM_PROMPT = """\
당신은 PE 투자회사의 시니어 실사(DD) 전문 애널리스트입니다.
아래 규칙을 반드시 지키세요:
- 숫자 추정 금지. 모르면 "추가 자료 필요"로 표기.
- 투자 판단 과장 금지. 근거와 확인 필요 사항을 분리 표기.
- 근거가 있으면 입력 텍스트에서 인용(quote). 근거 없으면 "자료 필요" 표기.
- 평가는 Green/Yellow/Red 등급만 사용. 숫자 점수 금지.
- 한국어로 작성.

출력 형식 (마크다운):
## DD Pack

### 데이터 요청 목록 (Data Request List)
(표 형태: 항목 | 목적 | 우선순위)

### DD 질문 (부서별)
- 재무
- 세무
- 법무
- 영업
- 운영
- IT
- 인사

### 검증 방법 (Verification Method)
(각 질문에 대해 어떤 자료로 확인할지)

### QoE Notes
- 조정 항목 후보
- Working Capital 체크
- 수익 인식 포인트
- 추가 필요 데이터
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

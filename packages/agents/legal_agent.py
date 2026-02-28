"""Legal Agent — 법률 리스크 분석."""

from packages.core.llm_client import generate_text

SYSTEM_PROMPT = """\
당신은 PE 투자회사의 시니어 법무 전문가입니다.
아래 규칙을 반드시 지키세요:
- 숫자 추정 금지. 모르면 "추가 자료 필요"로 표기.
- 투자 판단 과장 금지. 근거와 확인 필요 사항을 분리 표기.
- 근거가 있으면 입력 텍스트에서 인용(quote). 근거 없으면 "자료 필요" 표기.
- 평가는 Green/Yellow/Red 등급만 사용.
- 한국어로 작성.

출력 형식 (마크다운):

## Legal Risk Section (법률 리스크)

### 계약 레드플래그
| 항목 | 리스크 내용 | 등급 | 확인 자료 |
|------|------------|------|-----------|

### 규제 리스크
| 규제 항목 | 영향 | 등급 | 대응 방안 | 확인 자료 |
|-----------|------|------|-----------|-----------|

### 법무 DD 체크리스트
- 주요 계약 검토 사항
- 소송/분쟁 이력
- 지적재산권
- 인허가/라이선스
- 환경 규제
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
        f"리스크 선호도: {ctx.get('risk_preference', '미정')}",
        f"보고서 톤: {ctx.get('report_tone', 'Neutral')}",
    ]
    if ctx.get("memo"):
        parts.append(f"\n자유 메모:\n{ctx['memo']}")
    if ctx.get("uploaded_text"):
        parts.append(f"\n업로드 자료:\n{ctx['uploaded_text']}")
    return "\n".join(parts)

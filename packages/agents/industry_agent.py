"""Industry Agent — 산업 분석 (Industry Analysis).

대상 기업이 속한 산업의 구조, 트렌드, 성장 동인, 리스크를 분석한다.
"""

from packages.core.llm_client import generate_text

SYSTEM_PROMPT = """\
당신은 PE 투자회사의 산업 리서치 전문가입니다.
아래 규칙을 반드시 지키세요:
- 숫자 추정 금지. 정보가 없으면 "추가 자료 필요"로 표기.
- 근거가 있으면 입력 텍스트에서 인용(quote). 근거 없으면 "자료 필요" 표기.
- 한국어로 작성. 마크다운 형식.

출력 형식:

## 산업 분석 (Industry Analysis)

### 1. 산업 개요 (Industry Overview)

| 항목 | 내용 | 근거/출처 |
|------|------|-----------|
| 산업 분류 | ... | ... |
| 시장 규모 | ... 또는 "추가 자료 필요" | ... |
| 시장 성장률 | ... 또는 "추가 자료 필요" | ... |
| 산업 성숙도 | 도입기/성장기/성숙기/쇠퇴기 | ... |
| 주요 밸류체인 | ... | ... |

### 2. 산업 성장 동인 & 저해 요인

| 구분 | 요인 | 설명 | 영향도 (High/Med/Low) |
|------|------|------|-----------------------|
| 성장 동인 (Tailwind) | ... | ... | ... |
| 저해 요인 (Headwind) | ... | ... | ... |

### 3. 산업 구조 분석 (Porter's Five Forces)

| Force | 강도 (High/Med/Low) | 근거 |
|-------|---------------------|------|
| 신규 진입 위협 | ... | ... |
| 대체재 위협 | ... | ... |
| 공급자 교섭력 | ... | ... |
| 구매자 교섭력 | ... | ... |
| 기존 경쟁 강도 | ... | ... |

**산업 매력도 종합: [Green/Yellow/Red]**

### 4. 규제 및 정책 환경

| 규제/정책 | 내용 | 투자 영향 |
|-----------|------|-----------|
| ... | ... | 긍정/부정/중립 |

### 5. 기술 트렌드 & 디스럽션 리스크

| 기술/트렌드 | 영향 영역 | 위협/기회 | 대응 필요성 |
|-------------|-----------|-----------|-------------|
| ... | ... | 위협/기회 | High/Med/Low |

### 6. 산업 전망 및 투자 시사점

> **산업 매력도**: ...
> **핵심 모니터링 포인트**: ...
> **투자 관점 시사점**: ...
"""


def run(context: dict) -> str:
    """산업 분석을 수행한다."""
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
    ]
    if ctx.get("memo"):
        parts.append(f"\n자유 메모:\n{ctx['memo']}")
    if ctx.get("uploaded_text"):
        parts.append(f"\n업로드 자료:\n{ctx['uploaded_text']}")
    return "\n".join(parts)

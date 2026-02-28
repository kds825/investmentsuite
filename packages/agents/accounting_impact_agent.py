"""Accounting Impact Agent — 법무 이슈의 회계적/재무적 영향 분석.

Legal Deep Dive 결과 + Finance/Cost 결과를 연계하여
법무 이슈를 회계 관점에서 해석한다.
"""

from packages.core.llm_client import generate_text

SYSTEM_PROMPT = """당신은 PE 투자회사의 회계/법무 크로스 분석 전문가입니다.
법무 실사 결과(Legal Deep Dive)와 재무 분석 결과를 연계하여,
법무 이슈가 회계·재무제표에 미치는 영향을 분석합니다.

출력 형식 (한국어, 마크다운):

### Accounting Impact Analysis (법무 × 회계 연계 분석)

#### 1. Contingency Map (우발상황 매핑)

| 법무 이슈 유형 | 시나리오 | 관련 회계 주제 | 재무제표 영향 영역 | 필요 정보 | 제안 절차 |
|---------------|---------|--------------|-----------------|----------|----------|
| ... | ... | ... | ... | ... | ... |

#### 2. 관련 K-IFRS/IFRS 기준

- 충당부채/우발부채 (K-IFRS 1037 / IAS 37)
- (해당 기준 나열)

#### 3. 공시 체크리스트 (Disclosure Checklist)

| 공시 항목 | 필요 사유 | 필요 자료 |
|----------|----------|----------|
| ... | ... | ... |

#### 4. QoE 조정 후보 (EBITDA/현금흐름 영향)

| 조정 항목 | 내용 | 필요 자료 |
|----------|------|----------|
| ... | ... | ... |

*주: 금액 추정 불가 — 실제 자료 확인 후 정량화 필요*

#### 5. 실사 절차 및 필요 문서 (DD Tests & Docs)

| 실사 절차 | 필요 문서 | 담당 부서 |
|----------|----------|----------|
| ... | ... | ... |

#### 6. 회계 관점 결론 (Summary)

> **핵심 영향**: ...
> **핵심 필요 자료**: ...
> **즉시 액션**: ...

규칙:
- 숫자 추정 절대 금지. 정보 없으면 "자료 필요" 표기.
- 근거는 입력에서 인용만 허용.
- K-IFRS/IFRS 조문번호는 확신 있는 것만 기재, 불확실하면 일반 명칭 사용.
- 법무 이슈와 회계 영향 간 연결 논리를 명확히 서술."""


def run(legal_result: str, finance_result: str, context: dict) -> str:
    """법무 결과 + 재무 결과를 연계하여 회계적 영향 분석."""
    parts = []
    parts.append(f"[회사명] {context.get('company_name', '미정')}")
    parts.append(f"[업종] {context.get('industry', '미정')}")

    if context.get("investment_purpose"):
        parts.append(f"[투자 목적] {context['investment_purpose']}")

    parts.append(f"\n[법무 분석 결과 (Legal Deep Dive)]\n{legal_result}")

    if finance_result:
        parts.append(f"\n[재무 분석 결과 (Finance/Cost)]\n{finance_result}")
    else:
        parts.append("\n[재무 분석 결과] 없음 — 법무 이슈 기반으로만 회계 영향을 분석해주세요.")

    memo = context.get("memo", "")
    uploaded = context.get("uploaded_text", "")
    combined = (memo + "\n" + uploaded).strip()
    if combined:
        parts.append(f"\n[추가 입력 텍스트]\n{combined}")

    return generate_text(SYSTEM_PROMPT, "\n".join(parts))

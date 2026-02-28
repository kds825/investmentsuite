"""Legal Deep Dive Agent — PE 투자 딜 실무 수준 법무 분석.

3가지 분석 함수:
  1. run_deal_killer  — Deal Killer 탐지
  2. run_coc_map      — Change of Control / Assignment Map
  3. run_indemnity    — Indemnity Summary Table
"""

from packages.core.llm_client import generate_text


# ═══════════════════════════════════════════
# 1. Deal Killer Detector
# ═══════════════════════════════════════════

DEAL_KILLER_SYSTEM = """당신은 PE 투자회사의 시니어 법무 전문가입니다.
투자 딜에서 **Deal Killer**가 될 수 있는 위험 조항을 탐지합니다.

분석 대상 조항 유형:
- Change of Control (지배구조 변경)
- Termination (계약 해지)
- Exclusivity (독점 조항)
- Non-compete (경업 금지)
- MAC / MAE (중대한 부정적 변경)
- Assignment Restriction (양도 제한)
- Consent / Approval 요건

출력 형식 (한국어, 마크다운):

### Deal Killer 분석

**전체 위험도: [Green/Yellow/Red]**

#### 탐지된 위험 조항

| # | 유형 | 요약 | 위험 이유 | 제안 대응 |
|---|------|------|-----------|-----------|
| 1 | ... | ... | ... | ... |

#### 근거 인용
- "..." (입력 텍스트에서 직접 인용만 허용)

#### 권고 액션
1. ...
2. ...

규칙:
- 숫자 추정 금지. 정보 없으면 "자료 필요"로 표시.
- 근거는 입력 텍스트에서 인용(quote)만 허용.
- Green/Yellow/Red 등급만 사용.
- 입력 정보가 부족하면 "추가 계약서/문서 필요" 표기."""


def run_deal_killer(context: dict) -> str:
    """Deal Killer 탐지 분석."""
    prompt = _build_prompt(context, "Deal Killer 탐지")
    return generate_text(DEAL_KILLER_SYSTEM, prompt)


# ═══════════════════════════════════════════
# 2. Change of Control / Assignment Map
# ═══════════════════════════════════════════

COC_MAP_SYSTEM = """당신은 PE 투자회사의 시니어 법무 전문가입니다.
투자 딜에서 **Change of Control(지배구조 변경)** 관련 계약 조항을 분석하여
딜 전/후 필요 액션을 정리합니다.

출력 형식 (한국어, 마크다운):

### Change of Control / Assignment Map

#### CoC 트리거 맵

| 계약/거래처 | CoC 트리거 여부 | 동의 필요 | 상대방 | 딜 전 액션 | 딜 후 액션 |
|------------|----------------|----------|--------|-----------|-----------|
| ... | Yes/No/불명 | Yes/No | ... | ... | ... |

#### 핵심 액션 아이템
1. ...
2. ...

#### 근거 인용
- "..." (입력 텍스트에서 직접 인용만 허용)

규칙:
- 정보 없으면 "자료 필요" 표기.
- 근거는 입력 텍스트 인용만 허용.
- 추정/가정 금지."""


def run_coc_map(context: dict) -> str:
    """Change of Control / Assignment Map 분석."""
    prompt = _build_prompt(context, "Change of Control Map")
    return generate_text(COC_MAP_SYSTEM, prompt)


# ═══════════════════════════════════════════
# 3. Indemnity Summary Table
# ═══════════════════════════════════════════

INDEMNITY_SYSTEM = """당신은 PE 투자회사의 시니어 법무 전문가입니다.
투자 딜의 **면책(Indemnity)** 조항을 분석하여 핵심 조건을 요약합니다.

출력 형식 (한국어, 마크다운):

### Indemnity Summary

#### 면책 조건 요약

| 항목 | 내용 |
|------|------|
| Cap (면책 한도) | ... 또는 "자료 필요" |
| Basket (면책 기준액) | ... 또는 "자료 필요" |
| De Minimis (최소 청구액) | ... 또는 "자료 필요" |
| Survival Period (생존기간) | ... 또는 "자료 필요" |
| Claim Process (청구 절차) | ... 또는 "자료 필요" |

#### 핵심 리스크
1. ...

#### 협상 포인트
1. ...

#### 근거 인용
- "..." (입력 텍스트에서 직접 인용만 허용)

규칙:
- 숫자 추정 금지. 정보 없으면 "자료 필요" 표기.
- 근거는 입력 텍스트 인용만 허용."""


def run_indemnity(context: dict) -> str:
    """Indemnity Summary 분석."""
    prompt = _build_prompt(context, "Indemnity Summary")
    return generate_text(INDEMNITY_SYSTEM, prompt)


# ═══════════════════════════════════════════
# 공통 프롬프트 빌더
# ═══════════════════════════════════════════

def _build_prompt(context: dict, analysis_type: str) -> str:
    """컨텍스트에서 사용자 프롬프트를 구성한다."""
    parts = [f"[분석 유형] {analysis_type}"]
    parts.append(f"[회사명] {context.get('company_name', '미정')}")
    parts.append(f"[업종] {context.get('industry', '미정')}")

    if context.get("investment_purpose"):
        parts.append(f"[투자 목적] {context['investment_purpose']}")
    if context.get("risk_preference"):
        parts.append(f"[리스크 선호] {context['risk_preference']}")

    memo = context.get("memo", "")
    uploaded = context.get("uploaded_text", "")
    combined = (memo + "\n" + uploaded).strip()

    if combined:
        parts.append(f"\n[입력 텍스트 / 계약서 내용]\n{combined}")
    else:
        parts.append("\n[입력 텍스트] 없음 — 일반적인 PE 투자 딜 기준으로 분석해주세요.")

    return "\n".join(parts)

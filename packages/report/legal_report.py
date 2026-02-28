"""법무 모듈 전용 리포트 생성."""

from datetime import datetime


def generate_legal_markdown(context: dict, results: dict) -> str:
    """법무 분석 결과를 마크다운 보고서로 생성한다."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    # 헤더
    lines.append(f"# 법무 분석 보고서 — {context.get('company_name', '미정')}")
    lines.append(f"*생성일: {now}*")
    lines.append("")

    # 기본 정보
    lines.append("## 기본 정보")
    lines.append(f"- **회사명**: {context.get('company_name', '미정')}")
    lines.append(f"- **업종**: {context.get('industry', '미정')}")
    if context.get("investment_purpose"):
        lines.append(f"- **투자 목적**: {context['investment_purpose']}")
    lines.append("")

    deep_dive = results.get("deep_dive", False)

    if deep_dive:
        # Deep Dive 결과
        if results.get("deal_killer"):
            lines += ["---", "", results["deal_killer"], ""]
        if results.get("coc_map"):
            lines += ["---", "", results["coc_map"], ""]
        if results.get("indemnity"):
            lines += ["---", "", results["indemnity"], ""]
    else:
        # 간단 분석 결과
        if results.get("basic"):
            lines += ["---", "", results["basic"], ""]

    # Accounting Impact
    if results.get("accounting_impact"):
        lines += ["---", "", results["accounting_impact"], ""]

    # 면책 조항
    lines.append("---")
    lines.append("")
    lines.append("*본 보고서는 AI가 생성한 초안이며, 전문가 검토가 필요합니다.*")
    lines.append(f"*PwC PE Tool Suite | {now}*")

    return "\n".join(lines)

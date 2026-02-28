"""Orchestrator — 보고서 모드에 따라 에이전트를 조율한다."""

from packages.core.llm_client import generate_text
from packages.agents import (
    dd_agent,
    consulting_agent,
    legal_agent,
    finance_cost_agent,
    exit_strategy_agent,
    industry_agent,
    competitor_agent,
)

# 모드별 에이전트 매핑
MODE_AGENTS = {
    "IC Memo": ["consulting", "industry", "competitor", "exit_strategy"],
    "Full DD Report": ["industry", "competitor", "consulting", "dd", "legal", "finance_cost", "exit_strategy"],
    "Legal + Finance Appendix": ["legal", "finance_cost"],
}

AGENT_MAP = {
    "industry": ("Industry Agent (산업분석)", industry_agent),
    "competitor": ("Competitor Agent (경쟁사)", competitor_agent),
    "dd": ("DD Agent (실사)", dd_agent),
    "consulting": ("Consulting Agent (전략)", consulting_agent),
    "legal": ("Legal Agent (법무)", legal_agent),
    "finance_cost": ("FinanceCost Agent (재무)", finance_cost_agent),
    "exit_strategy": ("ExitStrategy Agent (엑싯)", exit_strategy_agent),
}

SUMMARY_SYSTEM = """\
당신은 PE 투자회사의 투자위원회(IC) 보고서 작성 전문가입니다.
아래 에이전트 분석 결과를 종합하여 다음을 작성하세요 (한국어):

1) Executive Summary (핵심 요약)
2) IC-ready Summary Box:
   - 결론: 추천 / 보류 / 반대
   - 근거 3개
   - 핵심 리스크 3개
   - Deal Breaker 1~3개
3) Assumption Log (가정 목록):
   - 사용자가 준 정보
   - 사용자가 안 준 정보 (Unknown)
   - 보고서에서 사용한 판단 기준
4) Open Questions / Next Diligence Actions
5) Known / Unknown / Next Actions
6) Evidence 섹션 (근거 인용)

규칙:
- 숫자 추정 금지. 모르면 "추가 자료 필요" 표기.
- 과장 금지. 근거와 확인 필요 사항을 분리.
- 평가는 Green/Yellow/Red만 사용.
- Deal Breaker 조건이 하나라도 충족되면 Red.
- 등급 판단 기준을 명시하라.
"""


def run(context: dict, mode: str, progress_callback=None):
    """에이전트를 순차 실행하고 최종 요약을 생성한다.

    Args:
        context: 사용자 입력 딕셔너리
        mode: 보고서 모드
        progress_callback: (agent_name, status) 콜백

    Returns:
        dict with keys: summary, agent_results (dict of agent_key -> text)
    """
    agent_keys = MODE_AGENTS.get(mode, MODE_AGENTS["Full DD Report"])
    agent_results = {}

    for key in agent_keys:
        label, agent_module = AGENT_MAP[key]
        if progress_callback:
            progress_callback(label, "실행 중...")
        result = agent_module.run(context)
        agent_results[key] = result
        if progress_callback:
            progress_callback(label, "완료")

    # 종합 요약 생성
    if progress_callback:
        progress_callback("종합 요약 생성", "실행 중...")

    combined = "\n\n---\n\n".join(
        f"### {AGENT_MAP[k][0]}\n{v}" for k, v in agent_results.items()
    )
    user_prompt = (
        f"보고서 모드: {mode}\n"
        f"회사명: {context.get('company_name', '미정')}\n"
        f"업종: {context.get('industry', '미정')}\n"
        f"투자 목적: {context.get('investment_purpose', '미정')}\n"
        f"투자 기간: {context.get('investment_period', '미정')}\n"
        f"엑싯 선호: {context.get('exit_preference', '미정')}\n"
        f"리스크 선호도: {context.get('risk_preference', '미정')}\n\n"
        f"=== 에이전트 분석 결과 ===\n\n{combined}"
    )

    summary = generate_text(SUMMARY_SYSTEM, user_prompt)

    if progress_callback:
        progress_callback("종합 요약 생성", "완료")

    return {"summary": summary, "agent_results": agent_results}

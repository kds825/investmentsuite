"""회계 질의회신 RAG 챗 엔진."""

from packages.rag.vector_store import search
from packages.core.llm_client import generate_chat

_SYSTEM_PROMPT = """당신은 한국채택국제회계기준(K-IFRS) 전문가입니다.
사용자의 회계 관련 질문에 대해 제공된 질의회신 자료를 근거로 정확하고 전문적인 답변을 제공합니다.

규칙:
1. 제공된 질의회신 자료를 최우선 근거로 활용하세요.
2. 답변 마지막에 참고한 질의회신의 출처를 명시하세요.
3. 질의회신 자료에 직접적인 답이 없는 경우, 관련 기준서를 바탕으로 답변하되 "제공된 질의회신에 직접적인 내용은 없으나"라고 명시하세요.
4. 답변은 명확하고 구조적으로 작성하세요.
5. 한국어로 답변하세요."""


def answer(query: str, chat_history: list[dict] = None) -> dict:
    """RAG 기반 답변 생성.

    Returns:
        {"answer": str, "sources": [{"id", "category", "question", "source", "date"}]}
    """
    # 1. 관련 질의회신 검색
    retrieved = search(query, top_k=3)

    # 2. 컨텍스트 구성
    context_parts = []
    for i, doc in enumerate(retrieved, 1):
        context_parts.append(
            f"[참고자료 {i}]\n"
            f"출처: {doc['source']} ({doc['date']})\n"
            f"분류: {doc['category']}\n"
            f"질문: {doc['question']}\n"
            f"답변: {doc['answer']}"
        )
    context_text = "\n\n".join(context_parts)

    # 3. 메시지 구성
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]

    # 대화 히스토리 추가 (최근 10개까지)
    if chat_history:
        for msg in chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # 사용자 질문 + 검색 결과
    user_message = f"""다음 질의회신 자료를 참고하여 질문에 답변해주세요.

---참고 질의회신 자료---
{context_text}
---

질문: {query}"""

    messages.append({"role": "user", "content": user_message})

    # 4. LLM 호출
    answer_text = generate_chat(messages)

    # 5. 출처 정보 정리
    sources = [
        {
            "id": doc["id"],
            "category": doc["category"],
            "question": doc["question"],
            "source": doc["source"],
            "date": doc["date"],
        }
        for doc in retrieved
    ]

    return {"answer": answer_text, "sources": sources}

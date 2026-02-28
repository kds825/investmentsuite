"""LLM 클라이언트 — 프로바이더 무관 통합 인터페이스.

지원 프로바이더 (env만 바꾸면 즉시 전환):
  - OpenAI   : LLM_BASE_URL=https://api.openai.com/v1
  - Gemini   : LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
  - Claude   : LLM_BASE_URL=https://api.anthropic.com/v1/ (+ anthropic-version 헤더)
  - Ollama   : LLM_BASE_URL=http://localhost:11434/v1
  - LM Studio: LLM_BASE_URL=http://localhost:1234/v1
  - vLLM     : LLM_BASE_URL=http://localhost:8000/v1
  - 기타 OpenAI-compatible 엔드포인트

모든 프로바이더는 OpenAI SDK의 base_url 파라미터로 연결됩니다.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None
_client_config = ("", "")


def _get_client() -> OpenAI:
    """설정이 바뀌면 클라이언트를 재생성한다."""
    global _client, _client_config
    api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "ollama"))
    base_url = os.getenv("LLM_BASE_URL", os.getenv("OPENAI_API_BASE_URL", "http://localhost:11434/v1"))
    current_config = (api_key, base_url)
    if _client is None or current_config != _client_config:
        _client = OpenAI(api_key=api_key, base_url=base_url)
        _client_config = current_config
    return _client


def get_model() -> str:
    """현재 설정된 모델명을 반환한다."""
    return os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", "gpt-4"))


def generate_text(system_prompt: str, user_prompt: str) -> str:
    """LLM chat completion 호출. 실패 시 사용자 친화적 메시지를 반환한다."""
    model = get_model()
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM 호출 오류] {e}"


def generate_chat(messages: list) -> str:
    """메시지 리스트를 직접 받아 LLM chat completion 호출. 대화 히스토리 지원."""
    model = get_model()
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM 호출 오류] {e}"

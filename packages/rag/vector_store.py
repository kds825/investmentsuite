"""벡터 스토어 — ChromaDB 기반 회계 질의회신 검색."""

import json
import sys
from pathlib import Path

# Python 3.14+ ChromaDB Pydantic v1 호환 패치
# chroma_server_nofile 필드의 @validator가 필드 선언보다 먼저 나와
# PEP 649(deferred annotation evaluation)에서 타입 추론 실패
if sys.version_info >= (3, 14):
    try:
        from chromadb import config as _chroma_cfg
        _orig_settings = _chroma_cfg.Settings
        # Settings 클래스를 로드할 때 에러가 나는지 테스트
        try:
            _orig_settings()
        except Exception:
            # monkey-patch: __annotations__에 누락된 타입을 직접 주입
            from typing import Optional
            if not hasattr(_orig_settings, '__annotations__'):
                _orig_settings.__annotations__ = {}
            _orig_settings.__annotations__.setdefault('chroma_server_nofile', Optional[int])
    except Exception:
        pass

import chromadb
from chromadb.config import Settings

# 경로 설정
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "accounting_qa"
_SAMPLE_PATH = _DATA_DIR / "sample_qa.json"
_CHROMA_DIR = _DATA_DIR / "chroma_db"
_COLLECTION_NAME = "accounting_qa"

_client = None
_collection = None


def _get_collection():
    """ChromaDB 컬렉션 반환 (싱글턴)."""
    global _client, _collection
    if _collection is None:
        try:
            _client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
        except Exception:
            # Pydantic v2 호환 이슈 우회: Settings를 직접 지정
            settings = Settings(
                persist_directory=str(_CHROMA_DIR),
                anonymized_telemetry=False,
                is_persistent=True,
            )
            _client = chromadb.Client(settings)
        _collection = _client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def initialize_store():
    """샘플 JSON 데이터를 ChromaDB에 로드. 이미 데이터가 있으면 스킵."""
    collection = _get_collection()

    if collection.count() > 0:
        return collection.count()

    with open(_SAMPLE_PATH, "r", encoding="utf-8") as f:
        qa_data = json.load(f)

    ids = []
    documents = []
    metadatas = []

    for item in qa_data:
        ids.append(item["id"])
        # 검색용 문서: 질문 + 답변을 합쳐서 임베딩
        doc = f"[{item['category']}] {item['question']}\n{item['answer']}"
        documents.append(doc)
        metadatas.append({
            "category": item["category"],
            "question": item["question"],
            "answer": item["answer"],
            "source": item["source"],
            "date": item["date"],
        })

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return len(ids)


def search(query: str, top_k: int = 3) -> list[dict]:
    """쿼리와 유사한 질의회신 검색. 결과: [{"id", "category", "question", "answer", "source", "date", "distance"}]"""
    collection = _get_collection()

    if collection.count() == 0:
        initialize_store()

    results = collection.query(query_texts=[query], n_results=min(top_k, collection.count()))

    items = []
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        items.append({
            "id": results["ids"][0][i],
            "category": meta["category"],
            "question": meta["question"],
            "answer": meta["answer"],
            "source": meta["source"],
            "date": meta["date"],
            "distance": results["distances"][0][i] if results.get("distances") else None,
        })

    return items

"""벡터 스토어 — ChromaDB 기반 회계 질의회신 검색."""

import json
from pathlib import Path

import chromadb

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
        _client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
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

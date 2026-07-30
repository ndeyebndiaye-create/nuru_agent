"""Tests ciblés des filtres pédagogiques Qdrant et du repli Retriever."""
from types import SimpleNamespace

from backend.app.agents.retriever_agent import RetrieverAgent
from backend.app.rag.vector_indexer.qdrant_client import (
    QdrantClientWrapper,
    _build_query_filter,
)


def _conditions_by_key(query_filter):
    return {condition.key: condition for condition in query_filter.must}


def test_filter_with_classe_only_uses_exact_keyword_match():
    query_filter = _build_query_filter({"classe": "Terminale"})
    conditions = _conditions_by_key(query_filter)

    assert set(conditions) == {"classe"}
    assert conditions["classe"].match.value == "Terminale"


def test_filter_with_serie_only_includes_existing_equivalent_values():
    query_filter = _build_query_filter({"serie": "S1"})
    values = set(_conditions_by_key(query_filter)["serie"].match.any)

    assert {"S1", "s1", "TS1", "Ts1", "ts1"} <= values


def test_filter_with_classe_and_serie_combines_both_conditions():
    query_filter = _build_query_filter({"classe": "Terminale", "serie": "S1"})
    conditions = _conditions_by_key(query_filter)

    assert set(conditions) == {"classe", "serie"}
    assert conditions["classe"].match.value == "Terminale"
    assert "S1" in conditions["serie"].match.any


class _FakeRetriever:
    def __init__(self, filtered_result=None, filtered_error=None):
        self.filtered_result = filtered_result
        self.filtered_error = filtered_error
        self.calls = []

    def search_by_metadata(self, query, filters, top_k):
        self.calls.append(("filtered", filters))
        if self.filtered_error:
            raise self.filtered_error
        return self.filtered_result

    def search(self, query, top_k):
        self.calls.append(("fallback", None))
        return [{"text": "document de repli", "metadata": {}}]


def test_retriever_falls_back_when_filtered_qdrant_search_raises():
    retriever = _FakeRetriever(filtered_error=RuntimeError("Qdrant indisponible"))
    result = RetrieverAgent(retriever=retriever).retrieve("question")

    assert result["has_context"] is True
    assert [call[0] for call in retriever.calls] == ["filtered", "fallback"]


def test_retriever_falls_back_when_filtered_search_returns_no_result():
    retriever = _FakeRetriever(filtered_result=[])
    result = RetrieverAgent(retriever=retriever).retrieve("question")

    assert result["has_context"] is True
    assert [call[0] for call in retriever.calls] == ["filtered", "fallback"]


class _FakeIndexClient:
    def __init__(self):
        self.payload_schema = {"classe": object()}
        self.created = []

    def get_collection(self, collection_name):
        return SimpleNamespace(payload_schema=dict(self.payload_schema))

    def create_payload_index(self, collection_name, field_name, field_schema, wait):
        self.created.append(field_name)
        self.payload_schema[field_name] = object()


def test_payload_index_creation_is_idempotent_and_only_adds_missing_fields():
    wrapper = QdrantClientWrapper.__new__(QdrantClientWrapper)
    wrapper.client = _FakeIndexClient()
    wrapper.collection_name = "existing_collection"

    assert wrapper.ensure_filter_payload_indexes() == ["serie"]
    assert wrapper.ensure_filter_payload_indexes() == []
    assert wrapper.client.created == ["serie"]

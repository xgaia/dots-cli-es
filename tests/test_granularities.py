from dots_es.api.search import build_granularities_body


def test_granularities_are_scoped_to_the_selected_perimeter():
    body = build_granularities_body(
        "cartulaires", [{"terms": {"resource_id": ["NDRC-AB"]}}]
    )

    assert body["query"]["bool"]["filter"] == [
        {"term": {"type.keyword": "fragment"}},
        {"prefix": {"collection_facets": "cartulaires###"}},
        {"terms": {"resource_id": ["NDRC-AB"]}},
    ]
    assert body["aggregations"]["cite_types"] == {
        "terms": {"field": "citeType", "size": 100}
    }


def test_granularities_without_perimeter_scope_the_collection_only():
    body = build_granularities_body("cartulaires")

    assert body["query"]["bool"]["filter"] == [
        {"term": {"type.keyword": "fragment"}},
        {"prefix": {"collection_facets": "cartulaires###"}},
    ]

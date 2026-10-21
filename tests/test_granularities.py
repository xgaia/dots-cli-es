from dots_es.api.search import build_granularities_body


def test_granularities_apply_the_caller_must_and_filters():
    body = build_granularities_body(
        [{"term": {"type.keyword": "fragment"}}, {"match": {"content": "Guérard"}}],
        [
            {"prefix": {"collection_facets": "cartulaires###"}},
            {"terms": {"resource_id": ["NDRC-AB"]}},
        ],
    )

    assert body["query"]["bool"]["must"] == [
        {"term": {"type.keyword": "fragment"}},
        {"match": {"content": "Guérard"}},
    ]
    assert body["query"]["bool"]["filter"] == [
        {"prefix": {"collection_facets": "cartulaires###"}},
        {"terms": {"resource_id": ["NDRC-AB"]}},
    ]
    assert body["aggregations"]["cite_types"] == {
        "terms": {"field": "citeType", "size": 100}
    }


def test_granularities_without_clauses_are_unfiltered():
    body = build_granularities_body()

    assert body["query"]["bool"] == {"must": [], "filter": []}

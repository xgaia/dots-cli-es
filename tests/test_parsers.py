from dots_es.api.search import (
    build_collection_facet,
    build_facet_clause,
    extract_highlight_patterns,
    parse_filters_param,
    parse_query_param,
    parse_range_parameter,
)


def test_parse_query_param_empty():
    assert parse_query_param("") == []
    assert parse_query_param(None) == []


def test_parse_query_param_exact_phrase():
    result = parse_query_param('"la phrase"')
    assert result[0]["bool"]["minimum_should_match"] == 1
    assert all("match_phrase" in clause for clause in result[0]["bool"]["should"])


def test_parse_query_param_query_string():
    result = parse_query_param("foo bar")
    assert result[0]["query_string"]["default_operator"] == "AND"
    assert "resource_metadata.title" in result[0]["query_string"]["fields"]


def test_parse_query_param_alias():
    result = parse_query_param("title:foo", "notice")
    assert "resource_metadata.dublincore.title:foo" in result[0]["query_string"]["query"]


def test_parse_query_param_fulltext_fields():
    result = parse_query_param("foo", "fulltext")
    assert result[0]["query_string"]["fields"] == ["content", "title"]


def test_parse_filters_param():
    filters = parse_filters_param("resource_metadata.dublincore.creator:A|B")
    assert len(filters) == 1
    query_string = filters[0]["query_string"]
    assert query_string["query"] == "A OR B"
    assert query_string["fields"] == ["resource_metadata.dublincore.creator"]


def test_parse_filters_param_multiple():
    assert len(parse_filters_param("a:1,b:2")) == 2


def test_parse_filters_param_empty():
    assert parse_filters_param("") == []
    assert parse_filters_param("abc") == []


def test_extract_highlight_patterns():
    patterns = extract_highlight_patterns('"une phrase" mot AND title:x')
    types = [pattern["type"] for pattern in patterns]
    assert "phrase" in types
    assert "word" in types
    assert all(pattern["value"] != "AND" for pattern in patterns)


def test_build_facet_clause_single():
    assert build_facet_clause("f", ["a"]) == {"term": {"f": "a"}}


def test_build_facet_clause_and():
    clause = build_facet_clause("f", ["a", "b"])
    assert clause["bool"]["must"] == [{"term": {"f": "a"}}, {"term": {"f": "b"}}]


def test_build_facet_clause_match_any():
    assert build_facet_clause("f", ["a", "b"], match_any=True) == {
        "terms": {"f": ["a", "b"]}
    }


def test_build_collection_facet():
    facet = build_collection_facet("cid")
    assert facet["aggs"]["values"]["terms"]["field"] == "collection_facets"
    assert facet["filter"]["bool"]["filter"] == [
        {"term": {"resource_metadata.path_ids.keyword": "cid"}}
    ]


def test_parse_range_parameter(client):
    with client.application.test_request_context(
        "/search?range[resource_metadata.dublincore.created]=gte:1800,lte:1900"
    ):
        assert parse_range_parameter() == [
            {"resource_metadata.dublincore.created": {"gte": "1800", "lte": "1900"}}
        ]

from elasticsearch.exceptions import BadRequestError


def _get_body(es):
    return es.search.call_args.kwargs["body"]


def _get_index(es):
    return es.search.call_args.kwargs["index"]


def test_notice_uses_resource_index(client, es):
    client.get(
        "/api/1.0/search?query=&no-highlight&collectionId=theater&page[size]=25"
    )
    assert _get_index(es) == client.application.config["RESOURCE_INDEX"]
    body = _get_body(es)
    assert {"term": {"type.keyword": "Resource"}} in body["query"]["bool"]["must"]
    assert body["_source"] == ["resource_metadata", "temporal"]


def test_fulltext_uses_passage_index(client, es):
    client.get("/api/1.0/search?query=molier&collectionId=theater&page[size]=25")
    assert _get_index(es) == client.application.config["PASSAGE_INDEX"]
    body = _get_body(es)
    assert {"term": {"type.keyword": "fragment"}} in body["query"]["bool"]["must"]
    assert body["collapse"]["field"] == "resource_id"


def test_fulltext_sends_temporal_default_sort(client, es):
    client.get("/api/1.0/search?query=molier&collectionId=theater&page[size]=25")
    sort_keys = [list(criterion)[0] for criterion in _get_body(es)["sort"]]
    assert "temporal.temporal.dublincore.created_start" in sort_keys


def test_notice_has_no_default_sort(client, es):
    client.get(
        "/api/1.0/search?query=&no-highlight&collectionId=theater&page[size]=25"
    )
    assert _get_body(es)["sort"] == []


def test_search_error_returns_400(client, es):
    es.search.side_effect = Exception(
        "No mapping found for [temporal.temporal.dublincore.created_start] in order to sort on"
    )
    response = client.get(
        "/api/1.0/search?query=molier&collectionId=theater&page[size]=25"
    )
    assert response.status_code == 400
    assert "No mapping found" in response.get_data(as_text=True)


def test_notice_response_structure(client, es):
    response = client.get(
        "/api/1.0/search?query=&no-highlight&collectionId=theater&page[size]=25"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert {
        "data",
        "total_count",
        "facets",
        "highlight_patterns",
        "temporal",
        "collection_indexed",
        "duration",
    }.issubset(data.keys())
    assert data["total_count"] == 2
    assert data["data"][0]["resource_id"] == "theater_01"
    assert data["data"][0]["dublincore"]["title"] == "Titre"
    assert data["collection_indexed"] is True


def test_fulltext_response_structure(client, es):
    response = client.get(
        "/api/1.0/search?query=molier&collectionId=theater&page[size]=25"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert {
        "buckets",
        "bucket_count",
        "facets",
        "highlight_patterns",
        "temporal",
        "collection_indexed",
        "page",
        "page_size",
        "total_count",
    }.issubset(data.keys())
    bucket = data["buckets"][0]
    assert bucket["resource_id"] == "theater_01"
    assert bucket["hits"][0]["highlight"]["content"] == ["<mark>mot</mark>"]
    assert data["bucket_count"] == 1


def test_collection_indexed_checked_on_resource_index(client, es):
    client.get(
        "/api/1.0/search?query=&no-highlight&collectionId=theater&page[size]=25"
    )
    assert es.count.call_args.kwargs["index"] == client.application.config[
        "RESOURCE_INDEX"
    ]


def test_exclude_facets(client, es):
    response = client.get(
        "/api/1.0/search?query=&no-highlight&collectionId=theater"
        "&excludeFacets=dublinCore.creator&page[size]=25"
    )
    body = _get_body(es)
    assert "dct:creator" not in body["aggregations"]
    assert "dct:contributor" in body["aggregations"]
    assert "dublinCore.creator" not in response.get_json()["facets"]


def test_notice_without_collection_id_sends_null_scope_filter(client, es):
    client.get("/api/1.0/search?query=&no-highlight&page[size]=25")
    body = _get_body(es)
    assert {"term": {"resource_metadata.path_ids.keyword": None}} in body["query"][
        "bool"
    ]["filter"]

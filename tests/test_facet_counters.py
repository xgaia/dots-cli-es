from dots_es.api.search_fields import (
    SearchFieldType,
    build_self_excluded_facet_aggs,
    facet_es_field,
    facet_fields,
)


def _facet_filter(aggs, facet_id):
    return aggs[facet_id]["aggs"]["filtered"]["filter"]["bool"]


def test_a_facet_ignores_its_own_selection():
    must = [{"term": {"type.keyword": "Resource"}}]
    creator = {"term": {"resource_metadata.dublincore.creator.keyword": "Depoin"}}
    language = {"term": {"resource_metadata.dublincore.language.keyword": "fre"}}

    aggs = build_self_excluded_facet_aggs(
        must,
        [creator, language],
        {"dublinCore.creator": creator, "dublinCore.language": language},
    )

    assert _facet_filter(aggs, "dct:creator")["must"] is must
    assert _facet_filter(aggs, "dct:creator")["filter"] == [language]
    assert _facet_filter(aggs, "dct:language")["filter"] == [creator]


def test_every_metadata_facet_ignores_its_own_selection():
    fields = [f for f in facet_fields() if f.type == SearchFieldType.KEYWORD]
    clauses = {field.key: {"term": {facet_es_field(field): "x"}} for field in fields}

    aggs = build_self_excluded_facet_aggs([], list(clauses.values()), clauses)

    for field in fields:
        others = _facet_filter(aggs, field.id)["filter"]
        assert clauses[field.key] not in others
        assert len(others) == len(clauses) - 1


def test_a_facet_without_selection_keeps_every_filter():
    scope = {"prefix": {"collection_facets": "cartulaires###"}}

    aggs = build_self_excluded_facet_aggs([], [scope], {})

    assert _facet_filter(aggs, "dct:creator")["filter"] == [scope]

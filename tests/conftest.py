import pytest
from types import SimpleNamespace
from unittest.mock import patch

from dots_es.api import create_app


@pytest.fixture(scope="session")
def client():
    app = create_app(config_name="local")
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def fake_result():
    return {
        "hits": {
            "total": {"value": 2},
            "hits": [
                {
                    "_id": "theater_01",
                    "_source": {
                        "resource_id": "theater_01",
                        "resource_metadata": {
                            "dublincore": {"title": "Titre", "creator": ["A"]},
                        },
                        "temporal": {
                            "temporal.dublincore.created_start": 1800,
                        },
                        "collections": [],
                    },
                    "inner_hits": {
                        "fragments": {
                            "hits": {
                                "hits": [
                                    {
                                        "_source": {
                                            "passage_id": "p1",
                                            "title": "Titre",
                                            "level": 1,
                                            "ancestors": ["theater_01"],
                                            "citeType": "urn",
                                        },
                                        "highlight": {"content": ["<mark>mot</mark>"]},
                                    }
                                ]
                            }
                        }
                    },
                }
            ],
        },
        "aggregations": {
            "collections_fac": {"filtered": {"values": {"buckets": []}}},
            "collections": {"filtered": {"values": {"buckets": []}}},
            "filtered_resource_count": {"count": {"value": 1}},
        },
    }


@pytest.fixture
def es(client, fake_result):
    es_client = client.application.elasticsearch
    with patch.object(es_client, "search", return_value=fake_result) as mock_search, \
        patch.object(es_client, "count", return_value={"count": 1}) as mock_count, \
        patch("dots_es.api.search.get_temporal_fields", return_value=[]):
        yield SimpleNamespace(search=mock_search, count=mock_count)

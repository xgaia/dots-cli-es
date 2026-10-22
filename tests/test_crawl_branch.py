import asyncio

from dots_es import cli


def make_app(collections, resources):
    return type(
        "App",
        (),
        {
            "config": {"MAX_CONCURRENT_REQUESTS": 1},
            "thunderdots_results": {
                "collection_results": collections,
                "resource_results": resources,
            },
            "excluded_collections": set(),
            "index_stats": {
                "projects": 0,
                "collections": 0,
                "excluded_collections": 0,
                "resources": 0,
                "passages": 0,
                "bulk_es_errors": 0,
            },
        },
    )()


def collection(cid, members):
    return {"@id": cid, "@type": "Collection", "title": cid, "member": members}


def test_missing_resource_does_not_abort_crawl(monkeypatch):
    """ThunderDots omits resources whose document does not parse: the crawl
    must skip them and keep indexing the other members of the collection."""
    indexed = []

    async def fake_index(app, resource_id, collections, resource_metadata, client=None):
        indexed.append(resource_id)

    monkeypatch.setattr(cli, "index_resource_passages_async", fake_index)

    app = make_app(
        [
            collection(
                "R",
                [
                    {"@id": "ok", "@type": "Resource", "title": "Ok"},
                    {"@id": "broken", "@type": "Resource", "title": "Broken"},
                    {"@id": "ok2", "@type": "Resource", "title": "Ok2"},
                ],
            )
        ],
        [
            {"@id": "ok", "@type": "Resource", "title": "Ok"},
            {"@id": "ok2", "@type": "Resource", "title": "Ok2"},
        ],
    )

    asyncio.run(
        cli.crawl_branch(
            app=app,
            chain=["R"],
            chain_label=["R"],
            target_collections=None,
            visited=set(),
            semaphore=asyncio.Semaphore(1),
            parent_id="R",
        )
    )

    assert indexed == ["ok", "ok2"]

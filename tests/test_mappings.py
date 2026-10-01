import json
from pathlib import Path

MAPPINGS_DIR = Path(__file__).resolve().parent.parent / "dots_es" / "elasticsearch"


def _mappings(name):
    data = json.loads((MAPPINGS_DIR / f"{name}.conf.json").read_text())
    return data["mappings"]


def test_passage_has_content_term_vector():
    properties = _mappings("dots_passage")["properties"]
    assert properties["content"]["term_vector"] == "with_positions_offsets"


def test_passage_has_resource_metadata_dynamic():
    properties = _mappings("dots_passage")["properties"]
    assert properties["resource_metadata"]["dynamic"] is True


def test_resource_has_no_passage_only_fields():
    properties = _mappings("dots_resource")["properties"]
    for field in ("content", "ancestors", "fragment_metadata", "passage_id"):
        assert field not in properties

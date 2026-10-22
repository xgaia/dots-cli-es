import json
from importlib import resources

import pytest


@pytest.mark.parametrize("index", ["dots_fragments", "dots_resources"])
def test_strings_are_never_detected_as_dates(index):
    # With date detection, the first "1241-03" fixes the field as date and every "1160–1196" rejects its whole document
    with resources.files("dots_es").joinpath("elasticsearch", f"{index}.conf.json").open() as f:
        mappings = json.load(f)["mappings"]

    assert mappings["date_detection"] is False


def test_resource_mapping_only_keeps_read_collection_subfields():
    with resources.files("dots_es").joinpath("elasticsearch", "dots_resources.conf.json").open() as f:
        properties = json.load(f)["mappings"]["properties"]

    assert "level" not in properties
    assert set(properties["collections"]["properties"]) == {"collection_id"}


def test_collection_index_mapping_is_removed():
    # The collections index was written but never read: no mapping, no config key
    mapping = resources.files("dots_es").joinpath("elasticsearch", "dots_collections.conf.json")

    assert not mapping.is_file()


def test_fragments_do_not_store_resource_metadata():
    with resources.files("dots_es").joinpath("elasticsearch", "dots_fragments.conf.json").open() as f:
        properties = json.load(f)["mappings"]["properties"]

    assert not {"resource_metadata", "temporal", "collections"} & properties.keys()

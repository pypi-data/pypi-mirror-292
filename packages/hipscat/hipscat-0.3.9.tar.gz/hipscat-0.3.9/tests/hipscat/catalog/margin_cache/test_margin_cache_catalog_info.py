import dataclasses
import json

import pytest

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.margin_cache.margin_cache_catalog_info import MarginCacheCatalogInfo
from hipscat.io import file_io


def test_margin_cache_catalog_info(margin_cache_catalog_info_data, assert_catalog_info_matches_dict):
    info = MarginCacheCatalogInfo(**margin_cache_catalog_info_data)
    assert_catalog_info_matches_dict(info, margin_cache_catalog_info_data)


def test_str(margin_cache_catalog_info_data):
    correct_string = ""
    for name, value in margin_cache_catalog_info_data.items():
        correct_string += f"  {name} {value}\n"
    cat_info = MarginCacheCatalogInfo(**margin_cache_catalog_info_data)
    assert str(cat_info) == correct_string


def test_read_from_file(margin_cache_catalog_info_file, assert_catalog_info_matches_dict):
    cat_info_fp = file_io.get_file_pointer_from_path(margin_cache_catalog_info_file)
    catalog_info = MarginCacheCatalogInfo.read_from_metadata_file(cat_info_fp)
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "epoch",
        "ra_column",
        "dec_column",
        "primary_catalog",
        "margin_threshold",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    with open(margin_cache_catalog_info_file, "r", encoding="utf-8") as cat_info_file:
        catalog_info_json = json.load(cat_info_file)
        assert_catalog_info_matches_dict(catalog_info, catalog_info_json)


def test_required_fields_missing(margin_cache_catalog_info_data):
    required_fields = ["primary_catalog", "margin_threshold"]
    for required_field in required_fields:
        assert required_field in MarginCacheCatalogInfo.required_fields
    for field in required_fields:
        init_data = margin_cache_catalog_info_data.copy()
        init_data[field] = None
        with pytest.raises(ValueError, match=field):
            MarginCacheCatalogInfo(**init_data)


def test_type_missing(margin_cache_catalog_info_data):
    init_data = margin_cache_catalog_info_data.copy()
    init_data["catalog_type"] = None
    catalog_info = MarginCacheCatalogInfo(**init_data)
    assert catalog_info.catalog_type == CatalogType.MARGIN


def test_wrong_type(margin_cache_catalog_info_data, catalog_info_data):
    with pytest.raises(TypeError, match="unexpected"):
        unexpected_info = {**catalog_info_data, "invalid_key": "unknown"}
        MarginCacheCatalogInfo(**unexpected_info)

    with pytest.raises(ValueError, match=f"{CatalogType.MARGIN}"):
        init_data = margin_cache_catalog_info_data.copy()
        init_data["catalog_type"] = CatalogType.OBJECT
        MarginCacheCatalogInfo(**init_data)

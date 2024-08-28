from pathlib import Path

import pytest

from hipscat.io.file_io import (
    append_paths_to_pointer,
    directory_has_contents,
    does_file_or_directory_exist,
    find_files_matching_path,
    get_basename_from_filepointer,
    get_directory_contents,
    get_file_pointer_for_fs,
    get_file_pointer_from_path,
    is_regular_file,
    strip_leading_slash_for_pyarrow,
)
from hipscat.io.file_io.file_pointer import get_fs


def test_get_pointer_from_path(tmp_path):
    tmp_pointer = get_file_pointer_from_path(str(tmp_path))
    assert str(tmp_pointer) == str(tmp_path)


def test_get_basename_from_filepointer(tmp_path):
    catalog_info_string = tmp_path / "catalog_info.json"
    catalog_info_pointer = get_file_pointer_from_path(catalog_info_string)
    assert get_basename_from_filepointer(catalog_info_pointer) == "catalog_info.json"


def test_file_or_dir_exist(small_sky_dir):
    small_sky_pointer = get_file_pointer_from_path(small_sky_dir)
    assert does_file_or_directory_exist(small_sky_pointer)
    catalog_info_string = small_sky_dir / "catalog_info.json"
    catalog_info_pointer = get_file_pointer_from_path(catalog_info_string)
    assert does_file_or_directory_exist(catalog_info_pointer)


def test_file_or_dir_exist_false(small_sky_dir):
    small_sky_pointer = get_file_pointer_from_path(str(small_sky_dir) + "incorrect file")
    assert not does_file_or_directory_exist(small_sky_pointer)


def test_append_paths_to_pointer(tmp_path):
    test_paths = ["folder", "file.txt"]
    test_path = tmp_path / "folder" / "file.txt"
    tmp_pointer = get_file_pointer_from_path(str(tmp_path))
    assert append_paths_to_pointer(tmp_pointer, *test_paths) == str(test_path)


def test_is_regular_file(small_sky_dir):
    catalog_info_file = small_sky_dir / "catalog_info.json"
    assert is_regular_file(catalog_info_file)

    assert not is_regular_file(small_sky_dir)

    partition_dir = small_sky_dir / "Norder=0"
    assert not is_regular_file(partition_dir)


def test_find_files_matching_path(small_sky_dir):
    ## no_wildcard
    matching_files = find_files_matching_path(small_sky_dir, "catalog_info.json")
    assert len(matching_files) == 1

    matching_files_with_protocol = find_files_matching_path(
        small_sky_dir, "catalog_info.json", include_protocol=True
    )
    assert matching_files_with_protocol[0] != matching_files[0]
    assert matching_files[0] in matching_files_with_protocol[0]

    ## wilcard in the name (matches catalog_info and provenance_info)
    assert len(find_files_matching_path(small_sky_dir, "*.json")) == 2


def test_find_files_matching_path_directory(small_sky_order1_dir):
    assert len(find_files_matching_path(small_sky_order1_dir)) == 1

    ## wildcard in directory - will match all files at indicated depth
    assert len(find_files_matching_path(small_sky_order1_dir, "*", "*", "*")) == 4


def test_directory_has_contents(small_sky_order1_dir, tmp_path):
    assert directory_has_contents(small_sky_order1_dir)
    assert not directory_has_contents(tmp_path)


def test_get_directory_contents(small_sky_order1_dir, tmp_path):
    small_sky_contents = get_directory_contents(small_sky_order1_dir)

    small_sky_paths = [Path(p) for p in small_sky_contents]

    expected = [
        "Norder=1",
        "README.md",
        "_common_metadata",
        "_metadata",
        "catalog_info.json",
        "partition_info.csv",
        "point_map.fits",
        "provenance_info.json",
    ]

    expected = [small_sky_order1_dir / file_name for file_name in expected]

    assert small_sky_paths == expected

    assert len(get_directory_contents(tmp_path)) == 0


def test_get_fs():
    filesystem, _ = get_fs("file://")
    assert "file" in filesystem.protocol

    # this will fail if the environment installs lakefs to import
    with pytest.raises(ImportError):
        get_fs("lakefs://")

    with pytest.raises(ValueError):
        get_fs("invalid://")


def test_get_file_pointer_for_fs():
    test_abfs_protocol_path = get_file_pointer_from_path("abfs:///container/path/to/parquet/file")
    assert (
        get_file_pointer_for_fs("abfs", file_pointer=test_abfs_protocol_path)
        == "/container/path/to/parquet/file"
    )
    test_s3_protocol_path = get_file_pointer_from_path("s3:///bucket/path/to/catalog.json")
    assert get_file_pointer_for_fs("s3", file_pointer=test_s3_protocol_path) == "/bucket/path/to/catalog.json"
    test_local_path = get_file_pointer_from_path("/path/to/file")
    assert get_file_pointer_for_fs("file", file_pointer=test_local_path) == test_local_path
    test_local_protocol_path = get_file_pointer_from_path("file:///path/to/file")
    assert get_file_pointer_for_fs("file", file_pointer=test_local_protocol_path) == "/path/to/file"


def test_strip_leading_slash_for_pyarrow():
    test_leading_slash_filename = get_file_pointer_from_path("/bucket/path/test.txt")
    assert (
        strip_leading_slash_for_pyarrow(test_leading_slash_filename, protocol="abfs")
        == "bucket/path/test.txt"
    )
    test_non_leading_slash_filename = get_file_pointer_from_path("bucket/path/test.txt")
    assert (
        strip_leading_slash_for_pyarrow(test_non_leading_slash_filename, protocol="abfs")
        == "bucket/path/test.txt"
    )

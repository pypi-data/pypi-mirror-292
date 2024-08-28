"""Test construction (and de-construction) of the hipscat ID"""

import numpy as np
import numpy.testing as npt
import pytest

import hipscat.pixel_math.healpix_shim as hp
from hipscat.pixel_math.hipscat_id import (
    HIPSCAT_ID_HEALPIX_ORDER,
    compute_hipscat_id,
    healpix_to_hipscat_id,
    hipscat_id_to_healpix,
)


def test_single():
    """Single point. Adheres to specification."""
    result = compute_hipscat_id([5], [5])
    expected = [5482513871577022464]

    npt.assert_array_equal(result, expected)


def test_jagged_list():
    """Arrays of mismatched lengths."""
    with pytest.raises(ValueError):
        compute_hipscat_id([5, 1, 5], [5])


def test_short_list():
    """Multiple points that will sit in the same higher-order-pixel.

    There are a handful of points at (5,5), and these should be assigned
    hipscat_id in sequential order, starting at
    5482513871577022464 (0x4C15CD518F800000).

    Interspersed are points at (1,1), which will start at
    5476738131329810432 (0x4C0148503DC00000)
    """
    result = compute_hipscat_id([5, 1, 5], [5, 1, 5])
    expected = [
        5482513871577022464,
        5476738131329810432,  # out of sequence
        5482513871577022465,
    ]
    npt.assert_array_equal(result, expected)


def test_list():
    """Multiple points that will sit in the same higher-order-pixel.

    There are a handful of points at (5,5), and these should be assigned
    hipscat_id in sequential order, starting at
    5482513871577022464 (0x4C15CD518F800000).

    Interspersed are points at (1,1), which will start at
    5476738131329810432 (0x4C0148503DC00000)
    """
    result = compute_hipscat_id([5, 5, 5, 1, 5, 5, 5, 1, 5], [5, 5, 5, 1, 5, 5, 5, 1, 5])
    expected = [
        5482513871577022464,
        5482513871577022465,
        5482513871577022466,
        5476738131329810432,  # out of sequence
        5482513871577022467,
        5482513871577022468,
        5482513871577022469,
        5476738131329810433,  # out of sequence
        5482513871577022470,
    ]
    npt.assert_array_equal(result, expected)


def test_load():
    """Generate a kinda big array and make sure the method completes in under a second.
    If this method is failing due to timeouts, please refactor to keep within the time limit.
    """
    rng = np.random.default_rng(seed=800)
    test_num = 1_000_000

    ra_arr = rng.random(test_num)
    dec_arr = rng.random(test_num)
    result = compute_hipscat_id(ra_arr, dec_arr)

    assert len(result) == test_num


def test_hipscat_id_to_healpix():
    """Test the inverse operation"""
    ids = [
        5482513871577022464,
        5482513871577022465,
        5482513871577022466,
        5476738131329810432,  # out of sequence
        5482513871577022467,
        5482513871577022468,
        5482513871577022469,
        5476738131329810433,  # out of sequence
        5482513871577022470,
    ]

    result = hipscat_id_to_healpix(ids)

    expected = [
        0x1305735463E,
        0x1305735463E,
        0x1305735463E,
        0x130052140F7,
        0x1305735463E,
        0x1305735463E,
        0x1305735463E,
        0x130052140F7,
        0x1305735463E,
    ]

    npt.assert_array_equal(result, expected)


def test_hipscat_id_to_healpix_low_order():
    """Test the inverse operation"""
    ids = [
        5482513871577022464,
        5482513871577022465,
        5482513871577022466,
        5476738131329810432,  # out of sequence
        5482513871577022467,
        5482513871577022468,
        5482513871577022469,
        5476738131329810433,  # out of sequence
        5482513871577022470,
    ]

    result = hipscat_id_to_healpix(ids, target_order=4)

    expected = [1217, 1217, 1217, 1216, 1217, 1217, 1217, 1216, 1217]

    npt.assert_array_equal(result, expected)


def test_healpix_to_hipscat_id_single():
    orders = [3, 3, 4, 1]
    pixels = [0, 12, 1231, 11]
    pixels_at_high_order = [p * (4 ** (HIPSCAT_ID_HEALPIX_ORDER - o)) for o, p in zip(orders, pixels)]
    lon, lat = hp.pix2ang(
        [2**HIPSCAT_ID_HEALPIX_ORDER] * len(orders), pixels_at_high_order, nest=True, lonlat=True
    )
    actual_hipscat_ids = compute_hipscat_id(lon, lat)
    test_hipscat_ids = [healpix_to_hipscat_id(o, p) for o, p in zip(orders, pixels)]
    assert np.all(test_hipscat_ids == actual_hipscat_ids)


def test_healpix_to_hipscat_id_array():
    orders = [3, 3, 4, 1]
    pixels = [0, 12, 1231, 11]
    pixels_at_high_order = [p * (4 ** (HIPSCAT_ID_HEALPIX_ORDER - o)) for o, p in zip(orders, pixels)]
    lon, lat = hp.pix2ang(
        [2**HIPSCAT_ID_HEALPIX_ORDER] * len(orders), pixels_at_high_order, nest=True, lonlat=True
    )
    actual_hipscat_ids = compute_hipscat_id(lon, lat)
    test_hipscat_ids = healpix_to_hipscat_id(orders, pixels)
    assert np.all(test_hipscat_ids == actual_hipscat_ids)


def test_healpix_to_hipscat_id_offset():
    orders = [3, 3, 4, 1]
    pixels = [0, 0, 1231, 11]
    offsets = [0, 1, 0, 0]
    pixels_at_high_order = [p * (4 ** (HIPSCAT_ID_HEALPIX_ORDER - o)) for o, p in zip(orders, pixels)]
    lon, lat = hp.pix2ang(
        [2**HIPSCAT_ID_HEALPIX_ORDER] * len(orders), pixels_at_high_order, nest=True, lonlat=True
    )
    actual_hipscat_ids = compute_hipscat_id(lon, lat)
    test_hipscat_ids = healpix_to_hipscat_id(orders, pixels, offsets)
    assert np.all(test_hipscat_ids == actual_hipscat_ids)

#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

import pytest

from pydantic_core._pydantic_core import ValidationError


def test_iter(compute_pools, temp_cp, instance_family):
    for cp in compute_pools.iter(like=temp_cp.name):
        assert cp.name in (
            temp_cp.name.upper(),  # for upper/lower case names
        )
        assert cp.instance_family == instance_family
        assert cp.min_nodes == 1
        assert cp.max_nodes == 1

    compute_pools_names = [cp.name for cp in compute_pools.iter(like="test_%")]
    assert temp_cp.name.upper() in compute_pools_names

    compute_pools_names = [cp.name for cp in compute_pools.iter(starts_with="test_")]
    assert temp_cp.name.upper() not in compute_pools_names

    compute_pools_names = [cp.name for cp in compute_pools.iter(starts_with="TEST_")]
    assert temp_cp.name.upper() in compute_pools_names


def test_iter_limit(compute_pools):
    with pytest.raises(
        ValidationError,
    ):
        assert len(compute_pools.iter(starts_with="TEST_", limit=0)) == 0

    compute_pools_names = [cp.name for cp in compute_pools.iter(starts_with="TEST_", limit=1)]
    assert len(compute_pools_names) <= 1

    with pytest.raises(
        ValidationError,
    ):
        compute_pools.iter(starts_with="TEST_", limit=10001)

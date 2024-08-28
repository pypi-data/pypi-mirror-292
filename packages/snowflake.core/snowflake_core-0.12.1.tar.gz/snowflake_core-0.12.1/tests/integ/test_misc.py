#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#

import pytest

from snowflake.core.database import Database
from tests.utils import is_prod_version, random_string


@pytest.mark.min_sf_ver("99.99.99")
def test_should_never_run_in_prod(snowflake_version):
    # This might still run in dev (where the version contains non-numerals,
    # so check if it has non-numerals). If it does not, then this should never
    # run.
    if is_prod_version(snowflake_version):
        pytest.fail("This test should not have run in a production version.")


@pytest.mark.min_sf_ver("1.0.0")
def test_should_always_run():
    pass


@pytest.mark.internal_only
@pytest.mark.usefixtures("backup_database_schema")
def test_large_results(databases, set_params):
    # Create a new db because it would only have 2 schemas initially: information_schema and public,
    # which does not trigger large results in the first iteration
    new_db = Database(name=random_string(3, "test_database_$12create_"), kind="TRANSIENT")
    database = databases.create(new_db)
    try:
        # This is fetched without large results
        schema_list1 = sorted(list(map(lambda sch: sch.name, database.schemas.iter())))

        with set_params(parameters={"RESULT_FIRST_CHUNK_MAX_SIZE": 1}, scope="session"):
            # This will be fetched with large results because we force the first chunk size to be small.
            schema_list2 = sorted(list(map(lambda sch: sch.name, database.schemas.iter())))
            assert schema_list1 == schema_list2
    finally:
        database.drop()

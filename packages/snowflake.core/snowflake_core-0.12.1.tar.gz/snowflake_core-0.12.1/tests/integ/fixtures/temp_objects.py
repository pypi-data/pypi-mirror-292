from io import BytesIO
from textwrap import dedent
from typing import Iterator

import pytest

from snowflake.core.compute_pool import ComputePool
from snowflake.core.database import (
    Database,
    DatabaseCollection,
    DatabaseResource,
)
from snowflake.core.image_repository import ImageRepository
from snowflake.core.schema import (
    Schema,
    SchemaResource,
)
from snowflake.core.service import (
    Service,
    ServiceResource,
    ServiceSpecInlineText,
    ServiceSpecStageFile,
)

from ..utils import random_string
from .constants import TEST_SCHEMA


@pytest.fixture(scope="session", autouse=True)
def test_schema() -> str:
    """Set up and tear down the test schema. This is automatically called per test session."""
    return TEST_SCHEMA


@pytest.fixture
def temp_ir(image_repositories) -> Iterator[ImageRepository]:
    ir_name = random_string(5, "test_ir_")
    test_ir = ImageRepository(
        name=ir_name,
        # TODO: comment is not supported by image repositories?
        # comment="created by temp_ir",
    )
    image_repositories.create(test_ir)
    try:
        yield test_ir
    finally:
        image_repositories[test_ir.name].drop()


@pytest.fixture
def temp_cp(compute_pools, instance_family) -> Iterator[ComputePool]:
    cp_name = random_string(5, "test_cp_")
    test_cp = ComputePool(
        name=cp_name, instance_family=instance_family,
        min_nodes=1, max_nodes=1, comment="created by temp_cp"
    )
    compute_pools.create(test_cp)
    try:
        yield test_cp
    finally:
        compute_pools[test_cp.name].drop()


@pytest.fixture
def temp_service(root, services, session, imagerepo, shared_compute_pool) -> Iterator[ServiceResource]:
    stage_name = random_string(5, "test_stage_")
    s_name = random_string(5, "test_service_")
    session.sql(f"create temp stage {stage_name};").collect()
    spec_file = "spec.yaml"
    spec = f"@{stage_name}/{spec_file}"
    session.file.put_stream(
        BytesIO(
            dedent(
                f"""
                spec:
                  containers:
                  - name: hello-world
                    image: {imagerepo}/hello-world:latest
                  endpoints:
                  - name: default
                    port: 8080
                 """
            ).encode()
        ),
        spec,
    )
    test_s = Service(
        name=s_name,
        compute_pool=shared_compute_pool,
        spec=ServiceSpecStageFile(stage=stage_name, spec_file=spec_file),
        min_instances=1,
        max_instances=5,
        comment="created by temp_service",
    )
    s = services.create(test_s)
    try:
        yield test_s
    finally:
        s.drop()


@pytest.fixture
def temp_service_from_spec_inline(root, services, session, imagerepo, shared_compute_pool) -> Iterator[ServiceResource]:
    s_name = random_string(5, "test_service_")
    inline_spec = dedent(
        f"""
        spec:
          containers:
          - name: hello-world
            image: {imagerepo}/hello-world:latest
         """
    )
    test_s = Service(
        name=s_name,
        compute_pool=shared_compute_pool,
        spec=ServiceSpecInlineText(spec_text=inline_spec),
        min_instances=1,
        max_instances=1,
        comment="created by temp_service_from_spec_inline",
    )
    s = services.create(test_s)
    try:
        yield test_s
    finally:
        s.drop()

@pytest.fixture
@pytest.mark.usefixtures("backup_database_schema")
def temp_db(databases: DatabaseCollection) -> Iterator[DatabaseResource]:
    # create temp database
    db_name = random_string(5, "test_database_")
    test_db = Database(name=db_name, comment="created by temp_db")
    db = databases.create(test_db)
    try:
        yield db
    finally:
        db.drop()


@pytest.fixture
@pytest.mark.usefixtures("backup_database_schema")
def temp_db_case_sensitive(databases: DatabaseCollection) -> Iterator[DatabaseResource]:
    # create temp database
    db_name = random_string(5, "test_database_case_sensitive_")
    db_name_case_sensitive = '"' + db_name + '"'
    test_db = Database(name=db_name_case_sensitive, comment="created by temp_case_sensitive_db")
    db = databases.create(test_db)
    try:
        yield db
    finally:
        db.drop()


@pytest.fixture
@pytest.mark.usefixtures("backup_database_schema")
def temp_schema(schemas) -> Iterator[SchemaResource]:
    schema_name = random_string(5, "test_schema_")
    test_schema = Schema(
        name=schema_name,
        comment="created by temp_schema",
    )
    sc = schemas.create(test_schema)
    try:
        yield sc
    finally:
        sc.drop()


@pytest.fixture
@pytest.mark.usefixtures("backup_database_schema")
def temp_schema_case_sensitive(schemas) -> Iterator[SchemaResource]:
    schema_name = random_string(5, "test_schema_case_sensitive_")
    schema_name_case_sensitive = '"' + schema_name + '"'
    test_schema = Schema(
        name=schema_name_case_sensitive,
        comment="created by temp_schema_case_sensitive",
    )
    sc = schemas.create(test_schema)
    try:
        yield sc
    finally:
        sc.drop()

from operator import attrgetter


def test_iter(stages, temp_stage, temp_stage_case_sensitive):
    stage_names = tuple(
        map(
            attrgetter("name"),
            stages.iter(),
        )
    )
    assert any(
        map(
            lambda e: e in stage_names,
            (
                temp_stage.name.upper(),  # for upper/lower case names
            ),
        )
    )


def test_iter_like(stages, temp_stage, temp_stage_case_sensitive):
    stage_names = tuple(
        map(
            attrgetter("name"),
            stages.iter(like="test_stage%"),
        )
    )
    assert any(
        map(
            lambda e: e in stage_names,
            (
                temp_stage.name.upper(),  # for upper/lower case names
            ),
        )
    )

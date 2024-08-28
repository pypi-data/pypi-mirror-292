import pytest


def test_resume_and_suspend(dynamic_table_handle):
    assert dynamic_table_handle.fetch().scheduling_state == 'RUNNING'
    dynamic_table_handle.suspend()
    assert dynamic_table_handle.fetch().scheduling_state == 'SUSPENDED'
    dynamic_table_handle.resume()
    assert dynamic_table_handle.fetch().scheduling_state == 'RUNNING'

@pytest.mark.skip("Enable when the DT supports bind parameters")
def test_refresh(dynamic_table_handle):
    dynamic_table_handle.refresh()

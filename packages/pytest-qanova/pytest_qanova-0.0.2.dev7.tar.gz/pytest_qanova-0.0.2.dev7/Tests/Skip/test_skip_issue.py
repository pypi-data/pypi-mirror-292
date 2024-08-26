"""Simple example skipped test."""

import pytest

ID = 'ABC-1234'
REASON = 'some_bug'
TYPE = 'PB'


@pytest.mark.slow(reason="DB under construction")
@pytest.mark.issue(issue_id=ID, reason=REASON, issue_type=TYPE)
@pytest.mark.skip(reason='no way of currently testing this')
def test_simple_skip():
    assert False
    
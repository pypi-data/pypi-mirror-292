import pytest
# Fixture teardown failure


@pytest.fixture
def teardown_failure_fixture(request):
    def teardown():
        raise ValueError("Intentional fixture teardown failure")
    request.addfinalizer(teardown)


def test_teardown_failure(teardown_failure_fixture):
    assert True  # This test will pass, but teardown will fail
    
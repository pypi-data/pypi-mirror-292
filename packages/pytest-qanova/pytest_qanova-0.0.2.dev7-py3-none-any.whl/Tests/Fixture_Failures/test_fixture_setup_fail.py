import pytest

# Fixture setup failure


@pytest.fixture
def failing_fixture():
    raise ValueError("Intentional fixture setup failure")


def test_fixture_failure(failing_fixture):
    assert True  # This line won't be reached due to fixture failure
    
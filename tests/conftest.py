import pytest
import uuid


@pytest.fixture
def unique_name():
    return f"test_group_{uuid.uuid4().hex[:8]}"
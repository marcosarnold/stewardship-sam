import pytest

from app.db import load_table


@pytest.fixture(scope="session")
def constituents():
    return load_table("constituents")


@pytest.fixture(scope="session")
def gifts():
    return load_table("gifts")


@pytest.fixture(scope="session")
def interactions():
    return load_table("interactions")

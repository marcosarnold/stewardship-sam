import pytest

from app.context import Context
from app.db import load_table
from app.dismissals import clear_all


@pytest.fixture(autouse=True)
def _reset_dismissals():
    clear_all()
    yield
    clear_all()


@pytest.fixture(scope="session")
def constituents():
    return load_table("constituents")


@pytest.fixture(scope="session")
def gifts():
    return load_table("gifts")


@pytest.fixture(scope="session")
def interactions():
    return load_table("interactions")


@pytest.fixture(scope="session")
def staff():
    return load_table("staff")


@pytest.fixture(scope="session")
def opportunities():
    return load_table("opportunities")


@pytest.fixture(scope="session")
def degrees():
    return load_table("degrees")


@pytest.fixture(scope="session")
def activities():
    return load_table("activities")


@pytest.fixture(scope="session")
def context(constituents, gifts, interactions, staff, opportunities):
    return Context(
        constituents=constituents,
        gifts=gifts,
        interactions=interactions,
        staff=staff,
        opportunities=opportunities,
    )

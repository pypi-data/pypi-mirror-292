from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def output_folder() -> Path:
    return Path(__file__).parent.parent / "output"


@pytest.fixture(scope="session")
def fixtures_folder() -> Path:
    return Path(__file__).parent / "fixtures"

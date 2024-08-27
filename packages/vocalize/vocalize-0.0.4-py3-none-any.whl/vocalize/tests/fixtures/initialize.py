import pytest
from dotenv import load_dotenv


@pytest.fixture
def load_env():
    load_dotenv()

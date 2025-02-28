import pytest
from httpx import ASGITransport, AsyncClient

from api.lib.elasticsearch.elastic_search_client import ElasticsearchClient
from api.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
async def candidates_es_client():
    return ElasticsearchClient("candidates")


@pytest.fixture(scope="session")
async def jobs_es_client():
    return ElasticsearchClient("jobs")

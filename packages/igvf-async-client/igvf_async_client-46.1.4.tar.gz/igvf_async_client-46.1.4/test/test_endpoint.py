import pytest


@pytest.mark.asyncio
async def test_endpoint_test_async_igvf_api():
    from igvf_async_client import AsyncIgvfApi
    api = AsyncIgvfApi()
    result = await api.search(query='ABC')
    assert result.total > 2
    result = await api.search(query='ABC', type=['Software'])
    assert result.graph[0].actual_instance.type == ['Software', 'Item']

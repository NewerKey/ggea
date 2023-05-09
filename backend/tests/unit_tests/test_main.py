async def test_startup_asynchronous_backend_server(async_client):
    response = await async_client.get("/docs")
    assert response.status_code == 200


async def test_automated_testing(async_client):
    response = await async_client.get("/docs")
    assert False == True
    assert sum([1, 1, 1]) == 6
    assert response.status_code != 200

# automated tests for the endpoints of the account router
import loguru


async def test_read_accounts(async_client):
    # arrange & act
    response = await async_client.get("api/v1/accounts")
    # assert
    loguru.logger.debug(response)
    assert response.status_code == 200

# automated tests for the endpoints of the authentication router


async def test_signup_success(async_client):
    # arrange & act
    response = await async_client.post(
        "api/v1/auth/signup",
        json={"account_signup": {"username": "string", "email": "user1@example.com", "password": "!1Password"}},
    )
    # assert
    assert response.status_code == 201


async def test_signup_failure_same_username(async_client):
    # arrange
    await async_client.post(
        "api/v1/auth/signup",
        json={"account_signup": {"username": "user2", "email": "user2@example.com", "password": "!1Password"}},
    )
    # act
    response = await async_client.post(
        "api/v1/auth/signup",
        json={"account_signup": {"username": "user2", "email": "unique_email@example.com", "password": "!1Password"}},
    )
    # assert
    assert response.status_code != 201


async def test_signup_failure_same_email(async_client):
    # arrange
    await async_client.post(
        "api/v1/auth/signup",
        json={"account_signup": {"username": "user", "email": "user@example.com", "password": "!1Password"}},
    )
    # act
    response = await async_client.post(
        "api/v1/auth/signup",
        json={
            "account_signup": {"username": "unique_username", "email": "user@example.com", "password": "!1Password"}
        },
    )
    # assert
    assert response.status_code != 201


async def test_signup_failure_weak_password(async_client):
    response = await async_client.post(
        "api/v1/auth/signup",
        json={
            "account_signup": {"username": "unique_username", "email": "unique_email@example.com", "password": "weak"}
        },
    )
    assert response.status_code != 201


async def test_signin_success(async_client):
    # arrange
    user_object = {
        "username": "signin_user",
        "email": "signin_user@example.com",
        "password": "!1Password",
    }

    await async_client.post("api/v1/auth/signup", json={"account_signup": user_object})

    # act
    response = await async_client.post(
        "api/v1/auth/signin", json={"account_signin": {"username": "signin_user", "password": "!1Password"}}
    )

    # assert
    assert response.status_code == 202


async def test_signin_failure_wrong_password(async_client):
    # arrange
    user_object = {
        "username": "signin_user_fail",
        "email": "signin_user_fail@example.com",
        "password": "!1Password",
    }

    await async_client.post("api/v1/auth/signup", json={"account_signup": user_object})

    # act
    response = await async_client.post(
        "api/v1/auth/signin",
        json={
            "account_signin": {
                "username": "signin_user_fail",
                "email": "signin_user_fail@example.com",
                "password": "wrong_password",
            }
        },
    )

    # assert
    assert response.status_code == 400

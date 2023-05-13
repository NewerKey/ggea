import uuid
import loguru
import fastapi

from src.api.dependency.crud import get_crud
from src.api.dependency.header import get_auth_current_user
from src.models.db.account import Account
from src.models.schema.account import (
    AccountInDeletionResponse,
    AccountInRead,
    AccountInResponse,
    AccountInUpdate,
    AccountWithToken,
    AccountOutPublic,
)
from src.repository.crud.account import AccountCRUDRepository
from src.security.authorizations.jwt import jwt_manager
from src.utility.exceptions.base_exception import BaseException
from src.utility.exceptions.custom import EntityDoesNotExist
from src.utility.exceptions.http.http_4xx import (
    http_exc_400_bad_request,
    http_exc_401_unauthorized_request,
    http_exc_403_forbidden_request,
    http_exc_404_resource_not_found,
)
from src.utility.exceptions.http.http_5xx import http_exc_500_internal_server_error

router = fastapi.APIRouter(prefix="/account", tags=["account"])


@router.get(
    path="/all",
    name="accounts:get-all-accounts",
    response_model=list[AccountInResponse],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_all_accounts(
    account_crud: AccountCRUDRepository = fastapi.Depends(
        get_crud(AccountCRUDRepository)
    ),
) -> list[AccountInResponse]:
    db_account_list: list = list()

    try:
        db_accounts = await account_crud.read_accounts()
        for db_account in db_accounts:
            account = AccountOutPublic(**db_account.__dict__)
            db_account_list.append(account)
        return db_account_list

    except BaseException as e:
        raise await http_exc_500_internal_server_error(error_msg=e.error_msg)


@router.get(
    path="",
    name="accounts:get-current-account",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def retrieve_current_account_by_id(
    current_account: Account = fastapi.Depends(get_auth_current_user()),
) -> AccountInResponse:
    jwt_token = jwt_manager.generate_jwt(account=current_account)
    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token,
            hashed_password=current_account.hashed_password,
            **current_account.__dict__
        ),
    )


@router.put(
    path="",
    name="accounts:update-current-account",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def edit_current_user_by_id(
    account_update: AccountInUpdate,
    current_account: Account = fastapi.Depends(get_auth_current_user()),
    account_crud: AccountCRUDRepository = fastapi.Depends(
        get_crud(AccountCRUDRepository)
    ),
) -> AccountInResponse:
    if (
        account_update.username and account_update.username != current_account.username
    ) or (account_update.email and account_update.email != current_account.email):
        if not await account_crud.is_credentials_available(
            account_input=account_update
        ):
            raise await http_exc_400_bad_request(
                error_msg="Username or email already taken"
            )
    try:
        updated_db_account = await account_crud.update_account(
            AccountInRead(id=current_account.id), account_update=account_update
        )
        jwt_token = jwt_manager.generate_jwt(account=updated_db_account)

        return AccountInResponse(
            authorized_account=AccountWithToken(
                token=jwt_token,
                hashed_password=updated_db_account.hashed_password,
                **updated_db_account.__dict__
            ),
        )
    except BaseException as e:
        raise await http_exc_500_internal_server_error(error_msg=e.error_msg)


@router.delete(
    path="/{username}",
    name="accounts:delete-current",
    response_model=AccountInDeletionResponse,
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def remove_curren(
    username: str,
    current_account: Account = fastapi.Depends(get_auth_current_user()),
    account_crud: AccountCRUDRepository = fastapi.Depends(
        get_crud(AccountCRUDRepository)
    ),
) -> AccountInDeletionResponse:
    if username != current_account.username:
        raise await http_exc_403_forbidden_request(
            error_msg="Not authorized to access this account"
        )
    try:
        is_account_deleted = await account_crud.delete_account(id=current_account.id)
        return AccountInDeletionResponse(is_deleted=is_account_deleted)

    except BaseException as e:
        raise await http_exc_500_internal_server_error(error_msg=e.error_msg)


@router.get(
    path="/{username}",
    name="accounts:retrieve-current-account-by-username",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def retrieve_current_account(
    username: str, current_account: Account = fastapi.Depends(get_auth_current_user())
) -> AccountInResponse:
    if username != current_account.username:
        raise await http_exc_403_forbidden_request()

    jwt_token = jwt_manager.generate_jwt(account=current_account)
    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token,
            hashed_password=current_account.hashed_password,
            **current_account.__dict__
        ),
    )


@router.put(
    path="/update/{username}",
    name="accounts:update-current-account-by-username",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def edit_current_user(
    username: str,
    account_update: AccountInUpdate,
    current_account: Account = fastapi.Depends(get_auth_current_user()),
    account_crud: AccountCRUDRepository = fastapi.Depends(
        get_crud(AccountCRUDRepository)
    ),
) -> AccountInResponse:
    if username != current_account.username:
        raise await http_exc_403_forbidden_request()

    if (
        account_update.username and account_update.username != current_account.username
    ) or (account_update.email and account_update.email != current_account.email):
        if not await account_crud.is_credentials_available(
            account_input=account_update
        ):
            raise await http_exc_400_bad_request()

    updated_db_account = await account_crud.update_account(
        AccountInRead(username=current_account.username), account_update=account_update
    )
    jwt_token = jwt_manager.generate_jwt(account=updated_db_account)

    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token,
            hashed_password=updated_db_account.hashed_password,
            **updated_db_account.__dict__
        ),
    )

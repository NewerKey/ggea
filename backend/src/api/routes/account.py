import uuid

import fastapi

from src.api.dependency.crud import get_crud
from src.api.dependency.header import get_auth_current_user
from src.models.db.account import Account
from src.models.schema.account import AccountInDeletionResponse, AccountInResponse, AccountInUpdate, AccountWithToken
from src.repository.crud.account import AccountCRUDRepository
from src.security.authorizations.jwt import jwt_manager
from src.utility.exceptions.custom import EntityDoesNotExist
from src.utility.exceptions.http.http_5xx import http_exc_500_internal_server_error
from src.utility.exceptions.http.http_4xx import (
    http_exc_400_bad_request,
    http_exc_401_unauthorized_request,
    http_exc_403_forbidden_request,
    http_exc_404_resource_not_found,
)

router = fastapi.APIRouter(prefix="/accounts", tags=["accounts"])


@router.get(path="", name="accounts:retrieve-accounts", response_model=list[AccountInResponse])
async def retrieve_accounts(
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(AccountCRUDRepository)),
) -> list[AccountInResponse]:
    db_account_list: list = list()

    try:
        db_accounts = await account_crud.read_accounts()
        for db_account in db_accounts:
            jwt_token = jwt_manager.generate_jwt(account=db_account)
            account = AccountInResponse(
                authorized_account=AccountWithToken(
                    token=jwt_token, hashed_password=db_account.hashed_password, **db_account.__dict__
                ),
                is_otp_required=False,
            )
            db_account_list.append(account)
        return db_account_list
    
    except Exception as e:
        raise await http_exc_500_internal_server_error(error_msg=e.error_msg)


@router.get(
    path="/{id}",
    name="accounts:retrieve-current-account_by_id",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def retrieve_current_account_by_id(
    id: int, current_account: Account = fastapi.Depends(get_auth_current_user())
) -> AccountInResponse:
    if id != current_account.id:
        raise await http_exc_403_forbidden_request(error_msg="Not authorized to access this account")

    jwt_token = jwt_manager.generate_jwt(account=current_account)
    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token, hashed_password=current_account.hashed_password, **current_account.__dict__
        ),
    )


@router.put(
    path="/update/{id}",
    name="accounts:update-current-account_by_id",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def edit_current_user_by_id(
    id: int,
    account_update: AccountInUpdate,
    current_account: Account = fastapi.Depends(get_auth_current_user()),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(AccountCRUDRepository)),
) -> AccountInResponse:
    if id != current_account.id:
        raise await http_exc_403_forbidden_request(error_msg="Not authorized to access this account")

    if (account_update.username and account_update.username != current_account.username) or (
        account_update.email and account_update.email != current_account.email
    ):
        if not await account_crud.is_credentials_available(account_input=account_update):
            raise await http_exc_400_bad_request(error_msg="Username or email already taken")

    updated_db_account = await account_crud.update_account_by_id(id=current_account.id, account_update=account_update)
    jwt_token = jwt_manager.generate_jwt(account=updated_db_account)

    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token, hashed_password=updated_db_account.hashed_password, **updated_db_account.__dict__
        ),
    )


@router.delete(
    path="/delete/{id}",
    name="accounts:delete-current-account_by_id",
    response_model=AccountInDeletionResponse,
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def remove_current_account_by_id(
    id: uuid.UUID,
    current_account: Account = fastapi.Depends(get_auth_current_user()),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(AccountCRUDRepository)),
) -> AccountInDeletionResponse:
    if id != current_account.id:
        raise await http_exc_403_forbidden_request(error_msg="Not authorized to access this account")

    is_account_deleted = await account_crud.delete_account_by_id(id=id)
    return AccountInDeletionResponse(is_deleted=is_account_deleted)


@router.delete(
    path="/delete/{username}",
    name="accounts:delete-current-account-by-username",
    response_model=AccountInDeletionResponse,
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def remove_current_account(
    username: str,
    current_account: Account = fastapi.Depends(get_auth_current_user()),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(AccountCRUDRepository)),
) -> AccountInDeletionResponse:
    if username != current_account.username:
        raise await http_exc_403_forbidden_request()

    is_account_deleted = await account_crud.delete_account_by_username(username=username)
    return AccountInDeletionResponse(is_deleted=is_account_deleted)


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
            token=jwt_token, hashed_password=current_account.hashed_password, **current_account.__dict__
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
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(AccountCRUDRepository)),
) -> AccountInResponse:
    if username != current_account.username:
        raise await http_exc_403_forbidden_request()

    if (account_update.username and account_update.username != current_account.username) or (
        account_update.email and account_update.email != current_account.email
    ):
        if not await account_crud.is_credentials_available(account_input=account_update):
            raise await http_exc_400_bad_request()

    updated_db_account = await account_crud.update_account_by_username(
        username=current_account.username, account_update=account_update
    )
    jwt_token = jwt_manager.generate_jwt(account=updated_db_account)

    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token, hashed_password=updated_db_account.hashed_password, **updated_db_account.__dict__
        ),
    )

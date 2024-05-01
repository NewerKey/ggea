import fastapi
import pydantic
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.api.dependency.crud import get_crud
from src.config.setup import settings
from src.models.schema.account import AccountInRead
from src.repository.crud.account import AccountCRUDRepository
from src.security.authorizations.jwt import jwt_manager
from src.utility.exceptions.http.exc_403 import http_exc_403_forbidden_request

# in the documentation of FastAPI the root is simply named "/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def oauth2_get_current_user(
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(AccountCRUDRepository)),
    token: str = fastapi.Depends(oauth2_scheme),
):
    try:
        username, email = jwt_manager.retrieve_details_from_jwt(token=token)

        # TODO: Try to read the account from the db to double check that it exists
        return await account_crud.read_account(
            account_in_read=AccountInRead(username=username, email=pydantic.EmailStr(email))
        )
    except ValueError as value_error:
        raise await http_exc_403_forbidden_request() from value_error

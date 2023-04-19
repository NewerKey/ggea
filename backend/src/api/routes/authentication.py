import typing

import fastapi
import pyotp

from src.api.dependency.crud import get_crud
from src.models.db.account import Account
from src.models.schema.account import (
    AccountInOAuthSignIn,
    AccountInRead,
    AccountInResponse,
    AccountInSignin,
    AccountInSignout,
    AccountInSignoutResponse,
    AccountInSignup,
    AccountInSignupResponse,
    AccountWithToken,
)
from src.repository.crud.account import AccountCRUDRepository
from src.repository.crud.profile import ProfileCRUDRepository
from src.security.authorizations import two_factor_auth
from src.security.authorizations.jwt import jwt_manager
from src.security.authorizations.oauth2 import oauth2_get_current_user
from src.utility.exceptions.custom import EmailAlreadyExists, UsernameAlreadyExists
from src.utility.exceptions.http.exc_400 import (
    http_exc_400_credentials_bad_signin_request,
    http_exc_400_credentials_bad_signup_request,
)

router = fastapi.APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    path="/signup",
    name="auth:account-signup",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def account_registration_endpoint(
    account_signup: AccountInSignup = fastapi.Body(..., embed=True),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
    profile_crud: ProfileCRUDRepository = fastapi.Depends(get_crud(repo_type=ProfileCRUDRepository)),
) -> AccountInResponse:
    is_credential_available = await account_crud.is_credentials_available(account_input=account_signup)

    if not is_credential_available:
        raise await http_exc_400_credentials_bad_signup_request()

    new_account = await account_crud.create_account(account_signup=account_signup)
    new_profile = await profile_crud.create_profile(parent_account=new_account)
    jwt_token = jwt_manager.generate_jwt(account=new_account)
    return AccountInSignupResponse(
        authorized_account=AccountWithToken(
            token=jwt_token, hashed_password=new_account.hashed_password, **new_account.__dict__
        ),
        is_profile_created=True if new_profile else False,
    )


@router.post(
    path="/signin",
    name="auth:account-signin",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def account_login_endpoint(
    account_signin: AccountInSignin = fastapi.Body(..., embed=True),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
) -> AccountInResponse:
    try:
        logged_in_account = await account_crud.signin_account(account_signin=account_signin)
    except Exception:
        raise await http_exc_400_credentials_bad_signin_request()

    jwt_token = jwt_manager.generate_jwt(account=logged_in_account)
    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token, hashed_password=logged_in_account.hashed_password, **logged_in_account.__dict__
        )
    )


@router.post(
    path="/signout",
    name="auth:account-signout",
    response_model=AccountInSignoutResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def account_logout_endpoint(
    account_signout: AccountInSignout = fastapi.Body(..., embed=True),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
) -> AccountInSignoutResponse:
    try:
        logged_out_account = await account_crud.signout_account(account_signout=account_signout)
    except Exception:
        raise await http_exc_400_credentials_bad_signin_request()
    return AccountInSignoutResponse(
        username=logged_out_account.username, is_logged_out=logged_out_account.is_logged_in
    )


@router.post("/validate_credentials_and_otp", response_model=typing.Any)
async def validate_credentials_and_otp(
    form_data: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
    account_repo: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
) -> typing.Any:
    #! This is bad smell
    # I need to know if the account has 2FA enabled or not before I can validate the password,
    # because the password is passed together with the OTP token in the same field.

    is_otp_enabled = await account_repo.is_otp_enabled(username=form_data.username)

    if is_otp_enabled:
        password, otp_token = two_factor_auth.separate_password_and_otp(form_data.password)

    else:
        password = form_data.password

    account_in_db = await account_repo.signin_oauth_account(
        AccountInOAuthSignIn(username=form_data.username, password=password)
    )
    if not account_in_db:
        raise await http_exc_400_credentials_bad_signin_request()

    if account_in_db.is_otp_enabled:
        is_token_valid = two_factor_auth.validate_otp(otp_token, account_in_db.otp_secret)

        if not is_token_valid:
            raise await http_exc_400_credentials_bad_signin_request()

    logged_in_account = AccountInRead(**account_in_db.__dict__)

    jwt_token = jwt_manager.generate_jwt(account=logged_in_account)

    return {"access_token": jwt_token, "token_type": "bearer"}


@router.post("/otp/generate", response_model=typing.Any)
async def generate_otp(
    id: int,
    account_repo: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
    current_account: Account = fastapi.Depends(oauth2_get_current_user),
) -> typing.Any:
    otp_secret = pyotp.random_base32()
    otp_auth_url = pyotp.totp.TOTP(otp_secret).provisioning_uri(name="test", issuer_name="GGEA")

    if not id == current_account.id:
        raise fastapi.HTTPException(status_code=403, detail="Not allowed")

    updated_account = await account_repo.set_otp_details(
        account=current_account, otp_secret=otp_secret, otp_auth_url=otp_auth_url
    )

    if not updated_account:
        raise fastapi.HTTPException(status_code=500, detail="Failed to set otp details")

    return {"otp_secret": otp_secret, "otp_auth_url": otp_auth_url}


@router.post("/otp/verify", response_model=typing.Any)
async def verify_otp(
    id: int,
    otp_token: str,
    account_repo: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
    current_account: Account = fastapi.Depends(oauth2_get_current_user),
) -> typing.Any:
    if not id == current_account.id:
        raise fastapi.HTTPException(status_code=403, detail="Not allowed")

    totp = pyotp.TOTP(current_account.otp_secret)
    if not totp.verify(otp_token):
        raise fastapi.HTTPException(status_code=403, detail="Invalid OTP Token")

    updated_account = await account_repo.update_account(
        id=current_account.id, update_data={"is_otp_verified": True, "is_otp_enabled": True}
    )

    return {"message": "OTP Token Verified"}


@router.post("/otp/validate", response_model=typing.Any)
async def validate_otp(
    id: int,
    otp_token: str,
    account_repo: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
    current_account: Account = fastapi.Depends(oauth2_get_current_user),
) -> typing.Any:
    if not id == current_account.id:
        raise fastapi.HTTPException(status_code=403, detail="Not allowed")

    if not current_account.is_otp_verified:
        raise fastapi.HTTPException(status_code=403, detail="OTP not enabled")

    totp = pyotp.TOTP(current_account.otp_secret)
    if not totp.verify(otp_token, valid_window=1):
        raise fastapi.HTTPException(status_code=403, detail="Invalid OTP Token")

    return {"opt_valid": True}

import datetime
import typing
from random import randint

import fastapi
import loguru
import pyotp
from fastapi import BackgroundTasks as FastApiBackgroundTasks
from slowapi import _rate_limit_exceeded_handler, Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.sql import functions as sqlalchemy_functions

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
    AccountInStateUpdate,
    AccountInVerification,
    AccountOutVerification,
    AccountWithToken,
)
from src.models.schema.otp import OtpIn, OtpInGenerateResponse, OtpInVerifyResponse
from src.repository.crud.account import AccountCRUDRepository
from src.repository.crud.profile import ProfileCRUDRepository
from src.security.authorizations import two_factor_auth
from src.security.authorizations.jwt import jwt_manager
from src.security.authorizations.oauth2 import oauth2_get_current_user
from src.utility.email.email_sender import send_email_background
from src.utility.exceptions.base_exception import BaseException
from src.utility.exceptions.custom import EmailAlreadyExists, UsernameAlreadyExists
from src.utility.exceptions.http.http_4xx import (
    http_exc_400_bad_request,
    http_exc_401_unauthorized_request,
    http_exc_403_forbidden_request,
    http_exc_404_resource_not_found,
)
from src.utility.exceptions.http.http_5xx import http_exc_500_internal_server_error

router = fastapi.APIRouter(prefix="/auth", tags=["authentication"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    path="/signup",
    name="auth:account-signup",
    response_model=AccountInSignupResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def account_signup_endpoint(
    request: fastapi.Request,
    background_tasks: FastApiBackgroundTasks,
    account_signup: AccountInSignup = fastapi.Body(..., embed=True),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
    profile_crud: ProfileCRUDRepository = fastapi.Depends(get_crud(repo_type=ProfileCRUDRepository)),
) -> AccountInSignupResponse:
    is_credential_available = await account_crud.is_credentials_available(account_input=account_signup)

    if not is_credential_available:
        raise await http_exc_400_bad_request(error_msg="Username or email is already taken")

    try:
        new_account = await account_crud.create_account(account_signup=account_signup)
        await profile_crud.create_profile(parent_account=new_account)

    except BaseException as e:
        loguru.logger.error(e)
        raise await http_exc_500_internal_server_error(error_msg="Failed to create account")

    send_email_background(
        background_tasks=background_tasks,
        email_to=new_account.email,
        body={"verification_code": new_account.verification_code},
    )

    return AccountInSignupResponse(username=new_account.username, email=new_account.email, is_profile_created=True)


@router.post(
    path="/signin",
    name="auth:account-signin",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
@limiter.limit("5/120seconds")
async def account_singin_endpoint(
    request: fastapi.Request,
    account_signin: AccountInSignin = fastapi.Body(..., embed=True),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
) -> AccountInResponse:
    try:
        logged_in_account = await account_crud.signin_account(account_signin=account_signin)
    except BaseException as e:
        raise await http_exc_400_bad_request(error_msg=e.error_msg)

    if logged_in_account.is_otp_enabled and logged_in_account.is_otp_verified:
        raise await http_exc_401_unauthorized_request(
            error_msg="Valid credentials but a OTP is required to finished the signin process"
        )

    jwt_token = jwt_manager.generate_jwt(account=logged_in_account)
    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token, hashed_password=logged_in_account.hashed_password, **logged_in_account.__dict__
        )
    )


@router.post(
    path="/account_verfication",
    name="auth:account-verfication",
    response_model=AccountOutVerification,
    status_code=fastapi.status.HTTP_200_OK,
)
@limiter.limit("5/120seconds")
async def account_verification(
    request: fastapi.Request,
    account_in_verification: AccountInVerification = fastapi.Body(..., embed=True),
    account_crud: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
) -> dict:
    try:
        is_verified = await account_crud.verify_account(account_in_verification=account_in_verification)
    except BaseException as e:
        raise await http_exc_400_bad_request(error_msg=e.error_msg)

    return AccountOutVerification(email=account_in_verification.email, is_verified=is_verified)


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
    except BaseException as e:
        raise await http_exc_400_bad_request(error_msg=e.error_msg)
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

    # is_otp_enabled = await account_repo.is_otp_enabled(username=form_data.username)

    # loguru.logger.debug(f"Is OTP enabled: {is_otp_enabled}")
    # if is_otp_enabled:
    #     password, otp_token = two_factor_auth.separate_password_and_otp(form_data.password)

    # else:
    #     password = form_data.password

    account_in_db = await account_repo.signin_oauth_account(
        AccountInOAuthSignIn(username=form_data.username, password=form_data.password)
    )
    if not account_in_db:
        raise await http_exc_403_forbidden_request(error_msg="Invalid credentials")

        # if account_in_db.is_otp_enabled:
        #     is_token_valid = two_factor_auth.validate_otp(otp_token, account_in_db.otp_secret)

        # if not is_token_valid:
        #     raise await http_exc_403_forbidden_request(error_msg="Invalid OTP token")

    logged_in_account = AccountInRead(**account_in_db.__dict__)

    jwt_token = jwt_manager.generate_jwt(account=logged_in_account)

    return {"access_token": jwt_token, "token_type": "bearer"}


@router.post(
    path="/otp",
    name="auth:otp-generate",
    response_model=dict,
    status_code=fastapi.status.HTTP_200_OK,
)
async def generate_otp(
    account_repo: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
    current_account: Account = fastapi.Depends(oauth2_get_current_user),
) -> dict:
    updated_account, otp_secret, otp_auth_url = await account_repo.set_otp_details(account=current_account)

    if not updated_account:
        raise await http_exc_500_internal_server_error(error_msg="Failed to generate OTP")

    return {"otp_secret": otp_secret, "otp_auth_url": otp_auth_url}


@router.put(
    path="/otp/verify",
    name="auth:otp-verify",
    response_model=dict,
    status_code=fastapi.status.HTTP_200_OK,
)
async def verify_otp(
    otp_in_verify: OtpIn = fastapi.Body(..., embed=True),
    account_repo: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
    current_account: Account = fastapi.Depends(oauth2_get_current_user),
) -> dict:
    if not otp_in_verify.email == current_account.email:
        raise await http_exc_403_forbidden_request(error_msg="Invalid email")

    totp = pyotp.TOTP(current_account.otp_secret)
    if not totp.verify(otp_in_verify.otp_token):
        raise await http_exc_403_forbidden_request(error_msg="Invalid OTP token")

    await account_repo.update_account(
        AccountInRead(id=current_account.id), account_update=AccountInStateUpdate(is_otp_verified=True)
    )

    return {"message": "OTP Token Verified"}


@router.put(
    path="/otp/validate",
    name="auth:otp-validate",
    response_model=AccountInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def validate_otp(
    otp_in_validate: OtpIn = fastapi.Body(..., embed=True),
    account_repo: AccountCRUDRepository = fastapi.Depends(get_crud(repo_type=AccountCRUDRepository)),
) -> AccountInResponse:
    try:
        current_account = await account_repo.read_account(AccountInRead(email=otp_in_validate.email))
    except BaseException:
        raise await http_exc_400_bad_request(error_msg="Invalid email")

    if not current_account.is_otp_verified:
        raise await http_exc_400_bad_request(error_msg="OTP not verified")

    if not current_account.is_logged_in:
        raise await http_exc_403_forbidden_request(error_msg="Account credentials not verified")

    if not current_account.otp_loggin_allowed():
        raise await http_exc_403_forbidden_request(error_msg="Account credentials verifeid too long ago, login again")

    if not two_factor_auth.validate_otp(otp_token=otp_in_validate.otp_token, otp_secret=current_account.otp_secret):
        raise await http_exc_403_forbidden_request(error_msg="Invalid OTP token")

    jwt_token = jwt_manager.generate_jwt(account=current_account)
    return AccountInResponse(
        authorized_account=AccountWithToken(
            token=jwt_token, hashed_password=current_account.hashed_password, **current_account.__dict__
        ),
        is_otp_required=False,
    )

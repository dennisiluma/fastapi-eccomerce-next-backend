import traceback

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from urllib.parse import urlencode
from app.core.config import settings
from app.db.session import get_session
from app.schemas.response import ApiResponse
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenData,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.google_auth import generate_user_token, process_google_callback_workflow
from app.services.user import login_user, process_forgot_password, process_reset_password, register_new_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, db: Session = Depends(get_session)
) -> ApiResponse[UserRead]:
    user = await register_new_user(db, user_data)

    return ApiResponse[UserRead](
        status=status.HTTP_201_CREATED,
        message="User Registered Successfully",
        data=user,
    )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    login_data: UserLogin, db: Session = Depends(get_session)
) -> ApiResponse[TokenData]:
    token_info = await login_user(db, login_data)

    return ApiResponse[TokenData](
        status=status.HTTP_200_OK,
        message="Login Successfully",
        data=token_info,
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(get_session)
) -> ApiResponse[None]:
    await process_forgot_password(db, request.email)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Reset Password Link Sent Successfully"
    )




@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest, db: Session = Depends(get_session)
) -> ApiResponse[None]:
    await process_reset_password(db, request)

    return ApiResponse[None](
        status=status.HTTP_200_OK,
        message="Password Reset Successfully"
    )


@router.get("/google")
async def google_login():

    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': f"{settings.BACKEND_URL}/api/auth/google/callback",
        'response_type': 'code',
        'scope': 'email profile',
        'access_type': 'offline',
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    print(f"🔐 Google login initiated")
    print(f"   Redirect URI: {params['redirect_uri']}")
    
    return RedirectResponse(url=auth_url)




@router.get("/google/callback")
async def google_callback(
    request: Request, 
    code: str = None,
    db: Session = Depends(get_session)
):
    print("=" * 60)
    print("📞 Google Callback Received")

    # Catch structural OAuth errors dropped as URL parameters early
    error = request.query_params.get('error')
    if error:
        print(f"❌ Google returned error: {error}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error={error}")
    
    if not code:
        print("❌ No authorization code received")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error=No authorization code")
    
    try:
        user = await process_google_callback_workflow(db, code)
        
        # Build app context tracking credentials
        auth_token = await generate_user_token(user)
        print(f"🔑 JWT token generated for user ID: {user.id}, Role: {user.role}")
        
        redirect_url = f"{settings.FRONTEND_URL}/auth-success?token={auth_token}&role={user.role}"
        print(f"🔄 Redirecting to: {redirect_url}")
        print("=" * 60)
        return RedirectResponse(url=redirect_url)
        
    except ValueError as val_err:
        print(f"⚠️ Validation error encountered during OAuth handling: {val_err}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error={str(val_err)}")
    except Exception as e:
        print(f"❌ ERROR in Google callback pipeline: {str(e)}")
        traceback.print_exc()
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-error?error=Unexpected authentication fault processing request.")





    

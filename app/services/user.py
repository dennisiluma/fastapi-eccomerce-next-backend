from datetime import datetime, timezone
from pathlib import Path
import secrets
import string
from unittest import result

from pwdlib import PasswordHash
from sqlmodel import Session, desc, select
from fastapi import UploadFile, status
from app.core.config import settings

from app.core.exceptions import ApiException
from app.core.security import create_access_token
from app.models.reset_code import ResetCode
from app.models.user import User
from app.schemas.user import PasswordUpdate, ResetPasswordRequest, TokenData, UserCreate, UserLogin, UserUpdate
from app.services.email import send_reset_password_email, send_welcome_email
from app.services.upload import upload_file, upload_to_s3

password_hasher = PasswordHash.recommended()



async def register_new_user(db: Session, user_data: UserCreate):

    statement = select(User).where(User.email == user_data.email)

    result = await db.exec(statement)

    if result.first():
        raise ApiException(
            message="User with this email already exisst",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    hashed_password = password_hasher.hash(user_data.password)

    user_to_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        role=user_data.role
    )

    db.add(user_to_user)
    await db.commit()
    await db.refresh(user_to_user)

    await send_welcome_email(user_to_user.email, user_to_user.name)

    return user_to_user




async def login_user(db: Session, login_data: UserLogin):
    # 1. Find user
    statement = select(User).where(User.email == login_data.email)
    result = await db.exec(statement)
    user = result.first()

    # 2. Verify password
    if not user or not password_hasher.verify(login_data.password, user.hashed_password):
        raise ApiException(
            message="Invalid email or password",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return TokenData(token=token, user=user)

    


async def process_forgot_password(db: Session, email:str):
    # 1. Verify user exists
    statement = select(User).where(User.email == email)
    result = await db.exec(statement)
    user = result.first()

    if not user:
        raise ApiException("User with this email not found", status.HTTP_404_NOT_FOUND)
    

    # 2. Generate a UNIQUE 6-character code
    unique_code = False
    code = ""

    while not unique_code:
        # Generate random uppercase 6-char string
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        # Check if this code already exists in the ResetCode table
        code_statement = select(ResetCode).where(ResetCode.code == code)
        existing_code = (await db.exec(code_statement)).first()
        
        if not existing_code:
            unique_code = True

    # 3. Save to DB
    reset_entry = ResetCode(email=email, code=code)
    db.add(reset_entry)
    await db.commit()

    reset_url = f"{settings.RESET_PASSWORD_URL}{code}"

    await send_reset_password_email(email, user.name, code, reset_url)
    return True



async def process_reset_password(db: Session, reset_data: ResetPasswordRequest):
    # 1. Find the code and check expiry
    statement = select(ResetCode).where(ResetCode.code == reset_data.code)
    reset_entry = (await db.exec(statement)).first()

    if not reset_entry:
        raise ApiException("Invalid reset code", status.HTTP_400_BAD_REQUEST)
    
    # Check if expired
    if datetime.now(timezone.utc).replace(tzinfo=None) > reset_entry.expires_at:
        raise ApiException("Reset code has expired", status.HTTP_400_BAD_REQUEST)
    

    # 2. Find the user
    user_stmt = select(User).where(User.email == reset_entry.email)
    user = (await db.exec(user_stmt)).first()

    if not user:
        raise ApiException("User no longer exists", status.HTTP_404_NOT_FOUND)
    
    # 3. Update Password
    user.hashed_password = password_hasher.hash(reset_data.password)
    db.add(user)

    # 4. Cleanup: Delete ALL codes for this email
    cleanup_stmt = select(ResetCode).where(ResetCode.email == reset_entry.email)
    codes_to_delete = (await db.exec(cleanup_stmt)).all()
    for c in codes_to_delete:
        await db.delete(c)
    
    await db.commit()
    return True



async def get_all_users_latest(db: Session):
    statement = select(User).order_by(desc(User.id))
    result = await db.exec(statement)
    return result.all()



async def update_user_profile(db: Session, user: User, update_data: UserUpdate):
    if update_data.name:
        user.name = update_data.name

    if update_data.address:
        user.address = update_data.address
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user



async def change_user_password(db: Session, user: User, password_data: PasswordUpdate):

    # 1. Verify old password
    if not password_hasher.verify(password_data.old_password, user.hashed_password):
        raise ApiException("Old password is incorrect", status.HTTP_400_BAD_REQUEST)
    

    # 2. Hash and update
    user.hashed_password = password_hasher.hash(password_data.new_password)
    db.add(user)
    await db.commit()
    return True




async def upload_profile_pix(db: Session, user: User, file: UploadFile):

    UPLOAD_DIR = Path("uploads/profile")

    # image_path = await upload_file(file, UPLOAD_DIR) #this will uplaod to your folder ehre

    image_path = await upload_to_s3(file, UPLOAD_DIR) #this will uplaod to aws s3
    user.profile_picture = image_path


    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return image_path
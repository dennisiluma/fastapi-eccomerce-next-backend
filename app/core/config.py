from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # --CORE SETTING --
    PROJECT_NAME: str = "Shope Ease"
    BACKEND_URL: str
    FRONTEND_URL: str

    # --- DATABASE --
    DATABASE_URL: str

    # JWT SECURITY VARIABLE
    SECRETE_JWT_KEY:str


    # SMTP EMAIL VARIABLES
    MAIL_USER:str
    MAIL_PASS:str
    MAIL_HOST:str
    MAIL_PORT:str
    MAIL_FROM:str
    
    DELIVERY_PERSON_EMAIL:str

    RESET_PASSWORD_URL:str

    # AWS VARIABLES
    AWS_ACCESS_KEY:str
    AWS_SECRET_KEY:str
    AWS_BUCKET_NAME:str

    # STRIPE
    STRIPE_SECRET_KEY:str

    PAYMENT_CONFIRMATION_URL:str
    PAYMENT_CANCEL_URL:str



    # -- LOAD CONFIGURATION --
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
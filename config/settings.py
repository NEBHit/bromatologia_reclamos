from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Mails
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_TLS: bool
    MAIL_SSL: bool

    # AUTH / SESSION
    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_SECONDS_EXP: int
    REFRESH_THRESHOLD: int

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
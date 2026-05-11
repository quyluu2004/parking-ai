from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "School Vehicle Management AI"
    DATABASE_URL: str = "postgresql://postgres:0948852292Aa@localhost:5432/school_parking"
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

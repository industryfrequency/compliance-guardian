from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    twelvelabs_api_key: str
    twelvelabs_index_name: str = "compliance-guardian-index"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-west-2"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:8000", "http://127.0.0.1:8000"]
    
    class Config:
        env_file = ".env"

settings = Settings()

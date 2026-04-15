from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    GOOGLE_MODEL_NAME: str
    OLLAMA_MODEL_NAME: str

    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
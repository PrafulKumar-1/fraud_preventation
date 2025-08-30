from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Suraksha API"
    API_V1_STR: str = "/api/v1"

    # --- External API Keys (load from environment variables) ---
    REALITY_DEFENDER_API_KEY: str = "your_reality_defender_api_key_here"

    # --- GCP Configuration ---
    GCP_PROJECT_ID: str = "project-suraksha-470515"

    class Config:
        case_sensitive = True


settings = Settings()
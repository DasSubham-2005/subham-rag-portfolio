from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Subham AI Portfolio API"
    database_url: str = "sqlite:///./portfolio.db"
    secret_key: str = "change-me"
    admin_username: str = "admin"
    admin_password: str = "ChangeMe123!"
    upload_dir: str = "uploads"
    chroma_dir: str = "chroma_db"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    cors_origins: str = "http://localhost:5173"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    contact_receiver_email: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    gemini_api_key: str = ""
    gemini_embedding_model: str = "gemini-embedding-001"
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_bucket: str = "portfoliouploads"

settings = Settings()

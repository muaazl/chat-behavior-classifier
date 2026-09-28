from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SPACY_MODEL: str = "en_core_web_sm"
    SENTIMENT_MODEL: str = "SamLowe/roberta-base-go_emotions"
    TOXICITY_MODEL: str = "unitary/unbiased-toxic-roberta"
    TOPIC_MODEL: str = "all-MiniLM-L6-v2"
    MAX_UPLOAD_BYTES: int = 10485760  # 10 MB limit
    THREAD_WORKERS: int = 2
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

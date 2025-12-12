from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    
    # Scraping
    scraping_timeout: int = 30
    max_content_length: int = 100000
    
    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Retrieval
    top_k_results: int = 5
    
    # LLM
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Resolve .env relative to this file's directory (backend/)
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # AWS
    aws_region: str = "ap-south-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # Bedrock
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # S3
    s3_bucket_name: str = "fasaldrishti-images"

    # DynamoDB
    dynamodb_table_users: str = "fasaldrishti-users"
    dynamodb_table_scans: str = "fasaldrishti-scans"

    # WhatsApp - Meta Cloud API (Option A)
    whatsapp_api_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "fasaldrishti_verify_2026"

    # WhatsApp - Twilio (Option B — recommended for hackathon)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""  # e.g. "whatsapp:+14155238886"

    # WhatsApp provider: "meta" or "twilio"
    whatsapp_provider: str = "twilio"

    # Public URL for webhook (ngrok, etc.)
    public_url: str = ""

    # App
    app_env: str = "development"
    app_port: int = 8000
    frontend_url: str = "http://localhost:5173"


@lru_cache()
def get_settings():
    return Settings()

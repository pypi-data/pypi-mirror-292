from universe_ai.config import Config as BaseConfig
import os


class Config(BaseConfig):
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    claude_model: str = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20240620')


def get_config() -> Config:
    return Config()
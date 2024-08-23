import os
from dotenv import dotenv_values, find_dotenv
from pydantic import BaseModel

ENV_NAME = os.environ.get("ENV_NAME", "dev")


class BaseConfig(BaseModel):
    ENV_NAME: str = "dev"
    APP_NAME: str

    OPENAI_API_KEY: str = "no key provided"

    ELEVEN_LABS_VOICE_ID: str = "no ID provided"
    ELEVEN_LABS_API_KEY: str = "no key provided"

    class Config:
        extra = "ignore"


_CONFIG: BaseConfig | None = None


def get_config(config_class: type[BaseModel]):
    global _CONFIG
    if _CONFIG is None:
        reload_config(config_class)
    return _CONFIG


def internal_get_loaded_config() -> BaseConfig:
    global _CONFIG
    if _CONFIG is None:
        raise ValueError("Config not loaded")
    return _CONFIG


def reload_config(config_class: type[BaseModel]):
    global _CONFIG
    print(f"Loading config for ENV_NAME={ENV_NAME}")
    _CONFIG = config_class.validate(load_config(ENV_NAME))
    print(f"Reloaded config")


def load_config(env_name: str) -> dict[str, any]:
    shared_path = find_dotenv(".env.shared", usecwd=True)

    if not shared_path:
        print("Using os.environ")
        return os.environ

    print(f"Loading {shared_path}")
    conf = {
        "ENV_NAME": env_name,
        **dotenv_values(find_dotenv(".env.shared_secrets", usecwd=True)),  # load shared secrets
        **dotenv_values(find_dotenv(".env.shared", usecwd=True)),  # load shared general variables
        **dotenv_values(find_dotenv(f".env.{env_name}", usecwd=True)),  # override with env-specific variables
        **os.environ,  # override with environment variables
    }
    return conf


# if ENV_NAME != "testing":
#     get_config()

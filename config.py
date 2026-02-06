from dotenv import load_dotenv
import os
from typing import List


load_dotenv()


class Settings:
    """Configurações da aplicação."""
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("PORT", os.getenv("APP_PORT", 8000)))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    match DEBUG:
        case True:
            ALLOWED_HOSTS: List[str] = ["*"]
        case False:
            ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "").split(",")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """Valida as configurações."""
        if not isinstance(cls.APP_PORT, int) or not (0 < cls.APP_PORT < 65536):
            raise ValueError("APP_PORT must be an integer between 1 and 65535.")
        if not isinstance(cls.ALLOWED_HOSTS, list):
            raise ValueError("ALLOWED_HOSTS must be a list of strings.")
        if cls.DEBUG not in [True, False]:
            raise ValueError("DEBUG must be a boolean value.")
        if cls.LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL.")
        
    @classmethod
    def get_info(cls) -> str:
        """Retorna uma string com as configurações atuais."""
        return {
            "APP_HOST": cls.APP_HOST,
            "APP_PORT": cls.APP_PORT,
            "DEBUG": cls.DEBUG,
            "ALLOWED_HOSTS": cls.ALLOWED_HOSTS,
            "LOG_LEVEL": cls.LOG_LEVEL,
        }

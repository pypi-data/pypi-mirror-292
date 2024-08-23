from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests.auth import HTTPBasicAuth

SODA_ENV_PREFIX = "CASTOR_SODA_"


class SodaCredentials(BaseSettings):
    """Class to handle Soda rest API permissions"""

    model_config = SettingsConfigDict(
        env_prefix=SODA_ENV_PREFIX,
        extra="ignore",
        populate_by_name=True,
    )

    api_key: str = Field(repr=False)
    secret: str = Field(repr=False)

    @property
    def reporting_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "API_KEY_ID": self.api_key,
            "API_KEY_SECRET": self.secret,
        }

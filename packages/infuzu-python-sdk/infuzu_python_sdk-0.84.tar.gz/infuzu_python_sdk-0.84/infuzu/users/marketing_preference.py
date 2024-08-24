from typing import Self
from pydantic import Field
from requests import Response
from .. import constants
from ..base import BaseInfuzuObject
from ..errors.base import InfuzuError
from ..http_requests import signed_requests
from ..utils.caching import CacheSystem


MARKETING_PREFERENCE_CACHE: CacheSystem = CacheSystem(default_expiry_time=600)


class MarketingPreference(BaseInfuzuObject):
    cogitobot_marketing_updates: bool | None = Field(frozen=True, default=None)

    @classmethod
    def field_names(cls) -> list[str]:
        return list(cls.model_fields.keys())

    @classmethod
    def retrieve(cls, user_id: str, force_new: bool = False) -> Self:
        def get_marketing_preference() -> MarketingPreference:
            api_response: Response = signed_requests.request(
                method="GET",
                url=f"{constants.USERS_BASE_URL}{constants.USERS_RETRIEVE_MARKETING_PREFERENCES_ENDPOINT}".replace(
                    '<str:user_id>', user_id
                )
            )
            if api_response.status_code == 200:
                return cls(**api_response.json())
            # TODO improve error handling
            raise InfuzuError(f"Error retrieving Marketing Preference: {api_response.text}")
        return MARKETING_PREFERENCE_CACHE.get(
            cache_key_name=f'retrieve-{user_id}',
            specialized_fetch_function=get_marketing_preference,
            force_new=force_new
        )

    @classmethod
    def update(cls, user_id: str, **fields) -> Self:
        for key, value in fields.items():
            if not isinstance(value, bool):
                raise TypeError(f"Invalid Type for {key}: {value}")

        def update_marketing_preference() -> MarketingPreference:
            api_response: Response = signed_requests.request(
                method="POST",
                url=f"{constants.USERS_BASE_URL}{constants.USERS_UPDATE_MARKETING_PREFERENCES_ENDPOINT}".replace(
                    '<str:user_id>', user_id
                ),
                json=fields
            )
            if api_response.status_code == 200:
                return cls(**api_response.json())
            # TODO improve error handling
            raise InfuzuError(f"Error retrieving Marketing Preference: {api_response.text}")
        return MARKETING_PREFERENCE_CACHE.get(
            cache_key_name=f'retrieve-{user_id}', specialized_fetch_function=update_marketing_preference, force_new=True
        )

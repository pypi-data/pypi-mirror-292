import json
from typing import Any

from aiohttp import ClientSession

from dictionary_wrapper.clients._wm_utils import form_url
from dictionary_wrapper.config import MWDictType
from dictionary_wrapper.exceptions import MerriamWebsterClientException


class AsyncMerriamWebsterClient:
    def __init__(self, word: str) -> None:
        self.word = word

    @staticmethod
    async def fetch_async(
        url, session: ClientSession, not_found_return_value: Any = None
    ):
        async with session.get(url) as response:
            if response.status != 200:
                content_text = await response.text()
                raise MerriamWebsterClientException(
                    status_code=response.status, content=content_text, url=url
                )

            if response.status == 404:
                return await not_found_return_value

            text_response = await response.text()

            return json.loads(text_response)

    async def get_api_result(
        self, session: ClientSession, dict_type: MWDictType, api_key: str
    ):
        url = form_url(self.word, dict_type, api_key)
        return await AsyncMerriamWebsterClient.fetch_async(url, session)

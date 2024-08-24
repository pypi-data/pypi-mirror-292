import json
from typing import Any

from aiohttp import ClientSession

from dictionary_wrapper import config
from dictionary_wrapper.clients._wordnik_utils import _parse_xml
from dictionary_wrapper.exceptions import WordnikClientException
from dictionary_wrapper.models.wordnik_models import WordnikAudio


class AsyncWordnikClient:
    def __init__(self, word: str, api_key: str) -> None:
        self.word = word
        self.api_key = api_key

    @staticmethod
    async def fetch_async(
        url, session: ClientSession, not_found_return_value: Any = None
    ) -> dict:
        async with session.get(url) as response:
            if response.status == 404:
                return not_found_return_value

            if response.status != 200:
                content_text = await response.text()
                raise WordnikClientException(
                    status_code=response.status, content=content_text, url=url
                )

            text_response = await response.text()

            return json.loads(text_response)

    async def extract_example_sentences(self, session: ClientSession):
        url = f"{config.WORDNIK_API_BASE_URL}/{self.word}/examples?includeDuplicates=false&useCanonical=false&limit=10&api_key={self.api_key}"
        response = await self.fetch_async(url, session)

        if response is None:
            return []

        sentence_objs = response.get("examples", [])

        sentences = [sentence_obj.get("text", "") for sentence_obj in sentence_objs]
        return list(filter(lambda x: len(x) > 0, sentences))

    async def extract_audio_link(self, session: ClientSession):
        url = f"{config.WORDNIK_API_BASE_URL}/{self.word}/audio?useCanonical=false&limit=50&api_key={self.api_key}"
        response_list = await self.fetch_async(url, session)

        if response_list is None:
            return None

        wordnik_audios = [WordnikAudio(**d) for d in response_list]

        macmillan = [w for w in wordnik_audios if w.createdBy == "macmillan"]

        return macmillan[0].fileUrl if len(macmillan) > 0 else wordnik_audios[0].fileUrl

    async def extract_etymologies(self, session: ClientSession):
        url = f"{config.WORDNIK_API_BASE_URL}/{self.word}/etymologies?useCanonical=false&api_key={self.api_key}"
        ety_list = await self.fetch_async(url, session, not_found_return_value=[])

        return [_parse_xml(ety) for ety in ety_list]

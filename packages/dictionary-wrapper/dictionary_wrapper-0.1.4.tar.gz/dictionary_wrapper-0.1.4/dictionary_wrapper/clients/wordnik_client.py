import requests  # type: ignore

import dictionary_wrapper.config as config
from dictionary_wrapper.clients._wordnik_utils import _parse_xml
from dictionary_wrapper.exceptions import WordnikClientException
from dictionary_wrapper.models.wordnik_models import WordnikAudio


class WordnikClient:
    def __init__(self, word: str, api_key: str) -> None:
        self.word = word
        self.api_key = api_key

    def extract_audio_link(self) -> str | None:
        url = f"{config.WORDNIK_API_BASE_URL}/{self.word}/audio?useCanonical=false&limit=50&api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise WordnikClientException(
                status_code=response.status_code, content=response.content, url=url
            )

        if response.status_code == 404:
            return None

        response_list = response.json()
        wordnik_audios = [WordnikAudio(**d) for d in response_list]

        macmillan = [w for w in wordnik_audios if w.createdBy == "macmillan"]

        return macmillan[0].fileUrl if len(macmillan) > 0 else wordnik_audios[0].fileUrl

    def extract_etymologies(self) -> list[str]:
        url = f"{config.WORDNIK_API_BASE_URL}/{self.word}/etymologies?useCanonical=false&api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise WordnikClientException(
                status_code=response.status_code, content=response.content, url=url
            )

        if response.status_code == 404:
            return []

        ety_list = response.json()

        return [_parse_xml(ety) for ety in ety_list]

    def extract_example_sentences(self) -> list[str]:
        url = f"{config.WORDNIK_API_BASE_URL}/{self.word}/examples?includeDuplicates=false&useCanonical=false&limit=10&api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise WordnikClientException(
                status_code=response.status_code, content=response.content, url=url
            )

        if response.status_code == 404:
            return []

        sentence_objs = response.json().get("examples", [])

        sentences = [sentence_obj.get("text", "") for sentence_obj in sentence_objs]
        return list(filter(lambda x: len(x) > 0, sentences))

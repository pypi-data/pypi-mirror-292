import asyncio

import aiohttp
from english_ipa.cambridge import CambridgeDictScraper  # type: ignore
from english_ipa.cambridge_async import AsyncCambridgeDictScraper  # type: ignore

from dictionary_wrapper.clients._wm_utils import (
    extract_audio_link,
    extract_definitions,
    extract_etymologies,
    extract_synonyms_or_antonyms,
)
from dictionary_wrapper.clients.mw_client import MerriamWebsterClient
from dictionary_wrapper.clients.mw_client_async import AsyncMerriamWebsterClient
from dictionary_wrapper.clients.wordnik_client import WordnikClient
from dictionary_wrapper.clients.wordnik_client_async import AsyncWordnikClient
from dictionary_wrapper.config import MWDictType
from dictionary_wrapper.models.common_models import WordField
from dictionary_wrapper.models.syn_ant_enum import SynAntEnum


def get_word_field(
    word: str, dictionary_api_key: str, thesaurus_api_key: str, wordnik_api_key: str
) -> WordField:
    mw_client = MerriamWebsterClient(word, dictionary_api_key, thesaurus_api_key)
    definitions = mw_client.extract_definitions()
    etymologies = mw_client.extract_etymologies()
    syns = mw_client.extract_synonyms_or_antonyms(SynAntEnum.Synonym)
    ants = mw_client.extract_synonyms_or_antonyms(SynAntEnum.Antonym)
    audio_link = mw_client.extract_audio_link()

    wordnik_client = WordnikClient(word, wordnik_api_key)
    sentences = wordnik_client.extract_example_sentences()

    scraper = CambridgeDictScraper()
    ipa_in_str = scraper.get_ipa_in_str(word)

    word_object = WordField(
        word=word,
        phonetic=ipa_in_str,
        definitions=definitions,
        etymologies=etymologies,
        synonyms=syns,
        antonyms=ants,
        exampleSentences=sentences,
        audioLink=audio_link,
    )

    return word_object


async def get_word_field_async(
    word: str, dictionary_api_key: str, thesaurus_api_key: str, wordnik_api_key: str
) -> WordField:
    wordnik_client = AsyncWordnikClient(word, wordnik_api_key)
    mw_client = AsyncMerriamWebsterClient(word)
    ipa_scraper = AsyncCambridgeDictScraper()
    async with aiohttp.ClientSession() as session:
        mw_dictionary = asyncio.create_task(
            mw_client.get_api_result(session, MWDictType.DICTIONARY, dictionary_api_key)
        )
        mw_thesaurus = asyncio.create_task(
            mw_client.get_api_result(session, MWDictType.THESAURUS, thesaurus_api_key)
        )
        sentences = asyncio.create_task(
            wordnik_client.extract_example_sentences(session)
        )
        ipa = asyncio.create_task(ipa_scraper.get_ipa_in_str(word))

        mw_dict, mw_thesaurus, sentences, ipa = await asyncio.gather(
            mw_dictionary, mw_thesaurus, sentences, ipa
        )

        return _get_word_field_from_request_result(
            word,
            mw_dict,
            mw_thesaurus,  # type: ignore
            sentences,  # type: ignore
            ipa,  # type: ignore
        )


def _get_word_field_from_request_result(
    word: str,
    mw_dict: list[dict],
    mw_thesaurus: list[dict],
    sentences: list[str],
    ipa: str,
) -> WordField:
    definitions = extract_definitions(word, mw_dict)
    etymologies = extract_etymologies(word, mw_dict)
    syns = extract_synonyms_or_antonyms(word, mw_thesaurus, SynAntEnum.Synonym)
    ants = extract_synonyms_or_antonyms(word, mw_thesaurus, SynAntEnum.Antonym)
    audio_link = extract_audio_link(mw_dict)

    word_object = WordField(
        word=word,
        phonetic=ipa,
        definitions=definitions,
        etymologies=etymologies,
        synonyms=syns,
        antonyms=ants,
        exampleSentences=sentences,
        audioLink=audio_link,
    )

    return word_object

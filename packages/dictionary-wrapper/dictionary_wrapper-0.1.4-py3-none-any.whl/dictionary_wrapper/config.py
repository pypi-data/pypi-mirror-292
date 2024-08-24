"""Configurations."""

from enum import Enum

from dotenv import load_dotenv

load_dotenv()

# merriam webster config
MW_BASE_URL = "https://dictionaryapi.com/api/v3/references"


class MWDictType(Enum):
    DICTIONARY = "collegiate"
    THESAURUS = "thesaurus"


MW_API_URL = {
    MWDictType.DICTIONARY.value: f"{MW_BASE_URL}/{MWDictType.DICTIONARY.value}/json",
    MWDictType.THESAURUS.value: f"{MW_BASE_URL}/{MWDictType.THESAURUS.value}/json",
}

MW_AUDIO_BASE_URL = "https://media.merriam-webster.com/audio/prons/en/us"
MW_AUDIO_FORMAT = "mp3"

# wordnik config
WORDNIK_API_BASE_URL = "https://api.wordnik.com/v4/word.json"

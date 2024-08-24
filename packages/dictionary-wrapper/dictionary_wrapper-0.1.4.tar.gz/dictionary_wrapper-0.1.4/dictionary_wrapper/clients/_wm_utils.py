import re
import string

from dictionary_wrapper.config import (
    MW_API_URL,
    MW_AUDIO_BASE_URL,
    MW_AUDIO_FORMAT,
    MWDictType,
)
from dictionary_wrapper.models.common_models import Definition, SynonymOrAntonym
from dictionary_wrapper.models.syn_ant_enum import SynAntEnum


def extract_audio_link(dictionary_result: list[dict]) -> str | None:
    first_def = dictionary_result[0]
    if not isinstance(first_def, dict):
        return None

    audio_dict = first_def.get("hwi")
    if audio_dict:
        pronoun_list = audio_dict.get("prs")
        if pronoun_list:
            sound_dict = pronoun_list[0].get("sound")
            if sound_dict:
                audio_id = sound_dict.get("audio")
                return __form_audio_link(audio_id, MW_AUDIO_FORMAT)

    return None


def __form_audio_link(audio_id: str, audio_format: str) -> str:
    sub_directory = __get_audio_subdirectory(audio_id)
    url = (
        f"{MW_AUDIO_BASE_URL}/{audio_format}/{sub_directory}/{audio_id}.{audio_format}"  # noqa: F821
    )
    return url


def __get_audio_subdirectory(audio_id: str) -> str:
    if len(audio_id) >= 3 and audio_id[:3] == "bix":
        return "bix"

    if len(audio_id) >= 2 and audio_id[:2] == "gg":
        return "gg"

    if audio_id[0].isnumeric() or (audio_id[0] in string.punctuation):
        return "number"

    return audio_id[0]


def extract_etymologies(word: str, dictionary_result: list[dict]) -> list[str]:
    etymologies_result = []
    for entry in dictionary_result:
        if not isinstance(entry, dict):
            continue

        if not _is_not_derived_entry(word, entry["meta"]["id"]):
            continue
        etymologies = entry.get("et", [])
        for etymology in etymologies:
            if etymology[0] == "text":
                ety_result = re.sub(r"\{it\}|\{/it\}", "", etymology[1])
                etymologies_result.append(ety_result)

    return etymologies_result


def extract_definitions(word: str, dictionary_result: list[dict]) -> list[Definition]:
    extracted_definitions: list[Definition] = []
    for entry in dictionary_result:
        if not isinstance(entry, dict):
            continue

        if not _is_not_derived_entry(word, entry["meta"]["id"]):
            continue
        part_of_speech = entry["fl"]
        definitions = entry["def"]
        for definition in definitions:
            sseqs = definition["sseq"]
            for sseq in sseqs:
                sense = sseq[0]
                type = sense[0]
                if type == "sense":
                    word_def = Definition(
                        partOfSpeech=part_of_speech, detail="", exampleSentence=""
                    )
                    dt = sense[1]["dt"]
                    for d in dt:
                        if d[0] == "text":
                            word_def.detail = clean_text(d[1])
                        elif d[0] == "vis":
                            sentences = d[1]
                            sentence = sentences[0]["t"]
                            word_def.exampleSentence = clean_text(sentence)
                    extracted_definitions.append(word_def)

    return extracted_definitions


def _is_not_derived_entry(word: str, id: str) -> bool:
    entry_word = id.split(":")[0]
    return entry_word.lower() == word


def extract_synonyms_or_antonyms(
    word: str, thesaurus_result: list[dict], type: SynAntEnum
) -> list[SynonymOrAntonym]:
    extracted_results = []
    for entry in thesaurus_result:
        if not isinstance(entry, dict):
            continue

        if not _is_not_derived_entry(word, entry["meta"]["id"]):
            continue
        part_of_speech = entry["fl"]
        definitions = entry["def"]

        syns_or_ants_lists = entry["meta"].get(type, [])
        extracted_syns_or_ants = [
            word for sublist in syns_or_ants_lists for word in sublist
        ]
        for definition in definitions:
            sseqs = definition["sseq"]
            for sseq in sseqs:
                sense = sseq[0]
                type = sense[0]
                if type == "sense":
                    word_def = SynonymOrAntonym(
                        partOfSpeech=part_of_speech,
                        detail="",
                        words=extracted_syns_or_ants,
                    )
                    dt = sense[1]["dt"]
                    for d in dt:
                        if d[0] == "text":
                            word_def.detail = d[1]

                    extracted_results.append(word_def)

    return extracted_results


def form_url(word: str, dict_type: MWDictType, api_key: str) -> str:
    base_url = MW_API_URL[dict_type.value]
    return base_url + f"/{word}?" + f"key={api_key}"


def clean_text(text: str) -> str:
    pattern1 = r"\{it\}|\{/it\}|\{wi\}|\{/wi\}|\{b\}|\{/b\|\{inf\}|\{/inf\}|\{sc\}|\{/sc\}|\{sup\}|\{/sup\}|\{gloss\}|\{/gloss\}|\{qword\}|\{/qword\}|\{phrase\}|\{/phrase\}|\{parahw\}|\{/qword\}|\{dx\}|\{/dx\}|\{dx_def\}|\{/dx_def\}|\{dx_ety\}|\{/dx_ety\}|\{ma\}|\{/ma\}"
    pattern2 = r"\{bc\}|\{ldquo\}|\{rdquo\}"

    pattern3 = r"\{[^|]*\|?|[{}|]"

    clean1 = re.sub(pattern1, "", text)
    clean2 = re.sub(pattern2, "", clean1)
    clean3 = re.sub(pattern3, "", clean2)
    return clean3

    clean1 = re.sub(pattern1, "", text)
    clean2 = re.sub(pattern2, "", clean1)
    clean3 = re.sub(pattern3, "", clean2)
    return clean3

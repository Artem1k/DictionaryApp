import pandas as pd
import re
import spacy
import contractions
import json
import os
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES

SETTINGS_PATH = "settings.json"


def extract_excel_subtitles(file_path: str) -> list:
    """
    Extract words from subtitles in an Excel file.
    Args:
        file_path (str): The path to the Excel file.
    Returns:
        list: A list of words extracted from the subtitles.
    """
    data = pd.read_excel(file_path)
    subtitles = data["Subtitle"].tolist()
    all_words = [word for subtitle in subtitles for word in nlp_func(subtitle)]
    return all_words


def nlp_func(text: str) -> list:
    """
    Process the text using spaCy to extract words and their parts of speech.
    Args:
        text (str): The input text to process.
        Returns:
        list: A list of lists, each containing a word and its part of speech.
    """
    doc, doc_list = nlp(contractions.fix(text)), []
    print(f"Processing text: {text}")
    for token in doc:
        lemma = token.lemma_
        pos = token.pos_
        token_text = token.text
        print(
            f"Token: {token_text}, POS: {pos}, Tag: {token.tag_}, ENt: {token.ent_type_}, Lemma: {lemma}"
        )
        if token.ent_type_ or (pos in ["PUNCT", "SPACE", "SYM", "NUM"]):
            continue
        if (lemma := re.sub(r"^[^\w]+|[^\w]+$", "", lemma)) != token.lemma_:
            if lemma == "":
                continue
        if len(lemma) < 2:
            continue
        if token.tag_ == "VBG" or lemma.lower().endswith("ing"):
            doc = nlp(lemma)
            pos = doc[0].pos_
            lemma = doc[0].lemma_
        if pos not in ("NOUN", "VERB", "ADJ", "ADV"):
            continue

        doc_list.append([lemma.lower(), pos])

    return doc_list


def translate_word(word: str, pos: str) -> str:
    if pos == "NOUN":
        article = "an" if bool(re.match(r"^[aeiouAEIOU]", word)) else "a"
        word = f"{article} {word}"
    elif pos == "VERB" or pos == "AUX":
        word = f"to {word}"

    try:
        return translator.translate(word).lower()
    except Exception:
        return "[error]"


def set_lang(lang: str = None):
    languages = {code: language for language, code in GOOGLE_LANGUAGES_TO_CODES.items()}
    print(languages)
    if lang:
        if lang in languages:
            print(f"Chosen language {languages[lang]}")
        else:
            return print(
                "Invalid language code. Please try again.(Available languages: "
                + ", ".join(languages.keys())
            )
    else:
        for code, language in languages.items():
            print(f"{code} - {language}")

        while True:
            lang = input("Input language code (e.g., 'uk' for Ukrainian): ").lower()
            if lang in languages:
                print(f"Chosen language {languages[lang]}")
                break
            else:
                print("Invalid language code. Please try again.")

        data = {"target_language": lang}
        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f)
    global translator
    translator = GoogleTranslator(source="en", target=lang)


def get_lang() -> None:
    if not os.path.exists(SETTINGS_PATH):
        return "uk"
    with open(SETTINGS_PATH) as f:
        data = json.load(f)
    return data.get("target_language", "uk")


try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")

# Translator
translator = GoogleTranslator(source="en", target=get_lang())

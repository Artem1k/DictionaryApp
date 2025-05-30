import pandas as pd
import re


def change_first_letter_to_lowercase(word):
    return re.sub(r'^[A-Z]', lambda x: x.group(0).lower(), word)

def extract_excel_subtitles(file_path):
    data = pd.read_excel(file_path)
    subtitles = data['Subtitle'].tolist()
    all_words = ' '.join(subtitles).split()  # The list of all words, with symbols, numbers etc.
    cleaned_words = [re.sub(r'^[^a-zA-Z]*|[^a-zA-Z]*$', '', word) for word in all_words]
    cleaned_words_from_none = list(filter(None, cleaned_words))
    lower_words = list(map(lambda lower: change_first_letter_to_lowercase(lower), cleaned_words_from_none))
    return lower_words

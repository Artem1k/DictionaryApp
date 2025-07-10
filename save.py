import pandas as pd
import csv
import shutil


categories = ['known', 'ignore', 'unknown']

def save(data: list, filename='unknown'):
    with open(f'{filename}.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        word_map = {row['Word']: int(row['Count']) for row in reader}

    for word in data:
        key = word[0]
        word_map[key] = word_map.get(key, 0) + int(word[1])

    sorted_items = sorted(word_map.items(), key=lambda item: item[1], reverse=True)
    rows = [{'Word': word, 'Count': count} for word, count in sorted_items]

    with open('unknown.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Word', 'Count'])
        writer.writeheader()
        writer.writerows(rows)

def save_to_new_file(data: list, filename, headers=["Word", "Count"]):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

def save_xlsx(data: list, name):
    pd.DataFrame(data, columns=["Word", "Count"])
    with pd.ExcelWriter(name, engine='openpyxl', mode='a') as writer:
        data.to_excel(writer, sheet_name='Words', index=False)

def to_add(word: list, filename='known'):
    with open(f'{filename}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(word)

def move_word_to_known(word: list):
    word_text = word[0]

    with open('unknown.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        word_pos_map = {row['Word']: idx for idx, row in enumerate(rows)}

    if (idx := word_pos_map.get(word_text)) is not None:
        word[1] += int(rows[idx]['Count'])
        del rows[idx]

        with open('unknown.csv', 'w', encoding='utf-8', newline='') as file_:
            writer = csv.DictWriter(file_, fieldnames=['Word', 'Count'])
            writer.writeheader()
            writer.writerows(rows)

    to_add(word=word)

def show_dict():
    with open('unknown.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        words = list(reader)
        print(pd.DataFrame(words, columns=["Word", "Count"]))

def import_dict(path):
    for category in categories:
        with open(f"{path}/{category}.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            words = [(row['Word'], int(row['Count'])) for row in reader]
        save(words, filename=category)


def export_dict(path):
    for category in categories:
        shutil.copy(f'dict/{category}.csv', f'{path}/{category}.csv')
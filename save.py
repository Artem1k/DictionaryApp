import pandas as pd
import csv
import shutil
import os


categories = ['known', 'ignore', 'unknown']

def save(data):
    word_map = {}
    with open('unknown.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            word_map[(row['Word'], row['Translation'])] = int(row['Count'])

    for word in data:
        key = (word[0], word[1])
        count = int(word[2])
        word_map[key] = word_map.get(key, 0) + count

    with open('unknown.csv', 'w', encoding='utf-8', newline='') as file:
        fieldnames = ['Word', 'Translation', 'Count']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for (word, translation), count in word_map.items():
            writer.writerow({'Word': word, 'Translation': translation, 'Count': count})

def save_to_new_file(data, filename='new.csv', headers=('word', 'translation', 'count')):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()  # Write the headers to the file
        for row in data:
            writer.writerow(row)

def save_xlsx(data):
    pd.DataFrame(data, columns=["Word", "Count"])
    with pd.ExcelWriter('subtitles.xlsx', engine='openpyxl', mode='a') as writer:
        data.to_excel(writer, sheet_name='Words', index=False)

def to_add(word, filename='known'):
    with open(f'{filename}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(word)

def move_word_to_known(word):
    word_text = word[0]

    with open('unknown.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        word_pos_map = {row['Word']: idx for idx, row in enumerate(rows)}

    if word_text in word_pos_map:
        idx = word_pos_map[word_text]
        word[1] += int(rows[idx]['Count'])
        del rows[idx]

        with open('unknown.csv', 'w', encoding='utf-8', newline='') as file_:
            fieldnames = ['Word', 'Translation', 'Count']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    to_add(word)

def show_dict():
    with open('unknown.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        words = list(reader)
        print(pd.DataFrame(words, columns=["Word", "Count"]))

def import_dict(path):
    def save_known():
        pass
    def save_ignore():
        pass
    def save_unknown():
        with open(f'{path}/unknown.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            words = [
                (row['Word'], row['Translation'], int(row['Count']))
                for row in reader
            ]
        save(words)
    for category in categories:
        exec(f"save_{category}()")


def export_dict(path):
    with open(f'{path}/unknown.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        words = list(reader)
        df = pd.DataFrame(words, columns=["Word", "Count"])
        df.to_csv(f'{path}/exported_unknown.csv', index=False)
    for category in categories:
        shutil.copy(f'dict/{category}.csv', f'{path}/{category}.csv')
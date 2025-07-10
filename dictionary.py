from collections import Counter
import extractor
import os
from save import *


class DictionaryApp:
    def __init__(self, words: list):
        self.words = words
        self.data = self.create()
        self.filter_words()
    
    def create(self):
        self.data = {category: [] for category in categories}

    def filter_words(self):
        word_to_category = {}

        for category in categories:
            with open(f'{category}.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    word_to_category[row['Word']] = category

        for word in self.words:
            category = word_to_category.get(word[0])
            self.data[category].append(word) if category else self.data['unknown'].append(word)

        self.words = []

    def show_dict(self):
        def get_valid_index(prompt):
            while True:
                try:
                    word = int(input(prompt + f"(1...{(length:=len(self.data['unknownwn']))}): "))
                    return word - 1 if 1 <= word <= length else print("Index out of range. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                except EOFError:
                    print("Input interrupted. Exiting...")
                    return None
            
        def handle_word_action(prompt, action):
            if idx := get_valid_index(prompt) is not None:
                action(self.data['unknown'].pop(idx))

        while True:
            print(pd.DataFrame(self.data['unknown'], columns=['Word', 'Count']))
            choice = input("Choose an option:\n1. Mark as known\n2. Mark as ignore\n3. Delay word\n\
                        4. Save to a separate dict file\n5. Save and exit\n6. Exit\n")
            match choice:
                case "1":
                    handle_word_action("Enter the word to mark as known", move_word_to_known)
                case "2":
                    handle_word_action("Enter the word to mark as ignore", lambda w: to_add(word=w, filename='ignore'))
                case "3":
                    handle_word_action("Enter the word to delay", lambda w: print(f"Word delayed: {w}"))
                case "4":
                    separate_file = input("Enter the name of the separate file(press 'Enter' for 'new.csv'): ") or 'new.csv'
                    save_to_new_file(data=self.data['unknown'], filename=separate_file)
                    print(f"Dictionary saved to {separate_file} successfully!")
                    break
                case "5":
                    save(data=self.data['unknown'])
                    print("Dictionary saved successfully!")
                    break
                case "6":
                    print("Exiting...")
                    self.create()
                    break
                case _:
                    print("Invalid choice. Try again.")

def invalid(text):
    while (choice := input(f"{text} (y/n): ").lower()) not in ('y', 'n'):
        print("Invalid input. Please enter 'y' or 'n'.")
    match choice:
        case 'y':
            return True
        case 'n':
            return False
        case _:
            raise ValueError("Unexpected input")

def make():
    path = input("Enter the path to the Excel file(or files with space between): ")
    files = path.split() if path.endswith('.xlsx') else [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.xlsx')]
    word_count_list = []
    for file in files:
        word_list = extractor.extract_excel_subtitles(file)
        save_xlsx(Counter(word_list).most_common(), file) if invalid("Save dict to the original file?") else print("Dict not saved to the original file.")
        word_count_list.extend(word_list)
    word_count = Counter(word_count_list).most_common()
    global words
    words = DictionaryApp(word_count)
    words.show_dict() if invalid("Show dict?") else print("Dict not shown.")

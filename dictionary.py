from collections import Counter
import extractor
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
            word_text = word[0]
            category = word_to_category.get(word_text)
            if category:
                self.data[category].append(word)
            else:
                self.data['unknown'].append(word)

        self.words = []

    def show_dict(self):
        def get_valid_index(prompt):
            try:
                word = int(input(prompt))
                if 1 <= word <= len(self.data['unknown']):
                    return word - 1
                else:
                    print("Index out of range.")
                    return None
            except ValueError:
                print("Invalid input. Please enter a number.")
                return None
            
        while True:
            print(pd.DataFrame(self.data['unknown'], columns=['Word', 'Count']))
            choice = input("Choose an option:\n1. Mark as known\n2. Mark as ignore\n3. Delay word\n\
                        4. Save to a separate dict file\n5. Save and exit\n6. Exit\n")
            match choice:
                case "1":
                    idx = get_valid_index(f"Enter the word to mark as known: (1...{len(self.data['unknown'])}) ")
                    if idx is not None:
                        move_word_to_known(self.data['unknown'].pop(idx))
                case "2":
                    idx = get_valid_index(f"Enter the word to mark as ignore: (1...{len(self.data['unknown'])}) ")
                    if idx is not None:
                        to_add(self.data['unknown'].pop(idx), 'ignore')
                case "3":
                    idx = get_valid_index(f"Enter the word to delay: (1...{len(self.data['unknown'])}) ")
                    if idx is not None:
                        print(f"Word delayed: {self.data['unknown'].pop(idx)}")
                case "4":
                    separate_file = input("Enter the name of the separate file: ")
                    save_to_new_file(self.data['unknown'], separate_file)
                    print(f"Dictionary saved to {separate_file} successfully!")
                    break
                case "5":
                    save(self.data['unknown'])
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
    return True if choice == 'y' else False

def make():
    path = input("Enter the path to the Excel file(or files with space between): ")
    files = path.split() if path.endswith('.xlsx') else [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.xlsx')]
    word_count_list = []
    for file in files:
        word_list = extractor.extract_excel_subtitles(file)
        word_count_list.extend(word_list)
    word_count = Counter(word_count_list)
    word_common = word_count.most_common()
    save_xlsx(word_common) if invalid("Save dict to the original file?") else print("Dict not saved to the original file.")
    global words
    words = DictionaryApp(word_common)
    words.show_dict() if invalid("Show dict?") else print("Dict not shown.")

import os
from collections import Counter
from dictaker import extractor, save, dictionary


def get_files(path: str) -> list:
    """Get a list of .xlsx files from the specified path."""

    files = []
    path_list = path.split()

    for new_path in path_list:
        clear_path = new_path.strip("\"'")
        if os.path.isfile(clear_path) and clear_path.endswith(".xlsx"):
            files.append(clear_path)
        elif os.path.isdir(clear_path):
            files.extend(
                [
                    os.path.join(clear_path, f)
                    for f in os.listdir(clear_path)
                    if f.endswith(".xlsx")
                ]
            )
        else:
            raise ValueError(
                "Path must be an .xlsx file or a directory containing .xlsx files"
            )

    if not files:
        raise FileNotFoundError("No .xlsx files found in the specified path")

    return files


def collect_words(files: list) -> list:
    """Collect words from the specified Excel files and return a list of word counts."""

    word_count_list = []
    for file in files:
        word_list = extractor.extract_excel_subtitles(file)
        (
            save.save_xlsx(Counter(word_list).most_common(), file)
            if input(f"Save dict to the original file({file})? (y/N): ").lower() == "y"
            else print("Dict not saved to the original file.")
        )
        word_count_list.extend(word_list)
    counter = Counter(tuple(lst) for lst in word_count_list)
    word_count = [list(k) + [v] for k, v in counter.most_common()]
    return word_count


def make() -> None:
    """Main function to create a dictionary from Excel files."""
    path = input("Enter the path to the Excel file(or folder with .xlsx files): ")
    files = get_files(path)
    word_count_list = collect_words(files)
    app = dictionary.DictionaryApp(words=word_count_list, files=files)
    app.run()


def show_dict() -> None:
    app = dictionary.DictionaryApp(for_db=True)
    app.run()

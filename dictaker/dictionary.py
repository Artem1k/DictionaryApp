import sqlite3
import pandas as pd
from dictaker import save, extractor


class DictionaryApp:
    """A class to manage a dictionary application that interacts with a SQLite database."""

    def __init__(self, words: list = [], files: list = [], for_db: bool = False):
        self.words = words
        self.files = files
        self.for_db = for_db
        self.known = False
        self.sort_key = "count"
        self.order = "DESC"
        self.category = "'Unknown', 'Deferred'"
        self.conn = sqlite3.connect("dictionary.db")

    def filter_words(self) -> None:
        """
        Filter words and insert them into the database.
        This method checks if the word already exists in the database and categorizes it accordingly, then adds to new_words table.
        If the word is new, it is translated and added to the new_words table.
        """

        filtered_words = {}

        for word, pos, count in self.words:
            translation, count_in_db, category = None, None, None

            rows = self.conn.execute(
                "SELECT translation, pos, count, category FROM words WHERE word = ?",
                (word,),
            ).fetchall()

            if rows:
                for row in rows:
                    if pos == row[1]:
                        translation, count_in_db, category = row[0], row[2], row[3]
                        break
                if not translation:
                    translation = extractor.translate_word(word, pos)
                    for row in rows:
                        if row[0] == translation:
                            count_in_db, category = row[2], row[3]
                            if count < count_in_db:
                                pos = row[1]
                            break
                    if not category:
                        count_in_db, category = 0, "Unknown"
            else:
                translation = extractor.translate_word(word, pos)
                count_in_db, category = 0, "Unknown"

            # This block is only executed for new words — a new combination of word and translation.
            if (key := (word, translation)) in filtered_words:
                new_count = filtered_words[key]["count"] + count
                filtered_words[key]["total_count"] = new_count
                filtered_words[key]["count"] = new_count

                if count > filtered_words[key]["max_count"]:
                    filtered_words[key]["pos"] = pos
                    filtered_words[key]["max_count"] = count
            else:
                if category == "Unknown" and count_in_db == 0:
                    print(f"New word found: {word} - {translation}")
                filtered_words[key] = {
                    "word": word,
                    "translation": translation,
                    "pos": pos,
                    "count": count,
                    "count_in_db": count_in_db,
                    "total_count": count + count_in_db,
                    "category": category,
                    "max_count": count,
                }

        for row in filtered_words.values():
            del row["max_count"]

        with self.conn:
            for row in filtered_words.values():
                save.insert_new_word(self.conn, *row.values())

    def insert_words(self) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO new_words (word, translation, pos, count, category) SELECT word, translation, pos, count, category FROM words"
            )

    def get_sql_template(self) -> str:
        return (
            f"SELECT word, translation, pos, count, count_in_db, total_count, category FROM new_words WHERE category in ({self.category})"
            + " ORDER BY {sort_key} {order}"
        )

    def check_unknown_words(self) -> None:
        query = (
            f"SELECT id, word, translation, pos, count, category FROM new_words ORDER BY {self.sort_key} {self.order}"
            if self.for_db
            else self.get_sql_template().format(
                sort_key=self.sort_key, order=self.order
            )
        )

        with self.conn:
            if rows := self.conn.execute(query).fetchall():
                self.words = {
                    (row[1], row[2]) if self.for_db else (row[0], row[1]): (
                        {
                            "id": row[0],
                            "word": row[1],
                            "translation": row[2],
                            "pos": row[3],
                            "count": row[4],
                            "category": row[5],
                        }
                        if self.for_db
                        else {
                            "word": row[0],
                            "translation": row[1],
                            "pos": row[2],
                            "count": row[3],
                            "count_in_db": row[4],
                            "total_count": row[5],
                            "category": row[6],
                        }
                    )
                    for idx, row in enumerate(rows)
                }
                return True
            words = "No words." if self.for_db else "No unknown words."
            print(words)
            return False

    def sort_words(self) -> None:
        """Sort the DataFrame. Sort options (sort by, ascending)"""

        if self.for_db:
            sort_options = ["id", "word", "pos", "count", "category"]
        else:
            sort_options = [
                "word",
                "pos",
                "count",
                "count_in_db",
                "total_count",
                "category",
            ]

        print("Sort by:")
        for i, option in enumerate(sort_options):
            print(f"{i}: {option}")

        option = sort_options.index("count")
        try:
            sort_key = int(
                input(
                    f"Choose a sort option from 0 to {len(sort_options) - 1}(default is {option}): "
                )
                or option
            )
        except ValueError:
            sort_key = option

        sort_key = (
            sort_options[sort_key]
            if 0 <= sort_key < len(sort_options)
            else self.sort_key
        )

        order = (
            "ASC"
            if input("Sort in ascending order? (y/N): ").lower() == "y"
            else "DESC"
        )

        self.sort_key = sort_key
        self.order = order

        self.check_unknown_words()

    def show_known_words(self) -> None:
        """Toggle between known and unknown words."""

        if "Known" in self.category:
            self.category = "'Unknown', 'Deferred'"
            self.known = False
            print("Known words hidden.")
        else:
            self.category = "'Unknown', 'Deferred', 'Known'"
            self.known = True
            print("Known words shown.")

        self.check_unknown_words()

    def save_to_separate_file(self) -> None:
        """Save the dictionary to a separate file."""

        separate_file = (
            input("Enter the name of the separate file (press 'Enter' for 'new.csv'): ")
            or "new.csv"
        )
        save.save_to_csv(data=self.words.values(), filename=separate_file)
        print(f"Dictionary saved to {separate_file} successfully!")

    def exit_only(self) -> None:
        """Exit the application without saving."""

        print("Exiting...")
        save.clean_up(self.conn)
        self.conn.close()

    def save_and_exit(self) -> None:
        """Save the dictionary to the database and exit."""

        if self.for_db:
            save.save_for_db(self.conn)
        else:
            save.save(self.conn, self.files)
        print("Dictionary saved successfully!")
        self.exit_only()

    def parse_number_ranges(self, s: str) -> list[int]:
        result = set()

        for part in s.split():
            try:
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    if start > end:
                        start, end = end, start
                    result.update(range(start, end + 1))
                else:
                    result.add(int(part))
            except ValueError:
                pass

        return sorted(result, reverse=True) if result else []

    def handle_word_action(self, prompt: str, category: str) -> None:
        """Move a word to a {category} category."""

        length = len(self.words)
        idx = input(f"{prompt} (0...{length}): ")
        for i in self.parse_number_ranges(idx):
            if 0 <= i < length:
                word = self.df.iloc[i]
                key = (word["word"], word["translation"])
                if self.for_db:
                    self.words[key]["category"] = category
                else:
                    del self.words[key]
                word, translation = key
                save.move_word(self.conn, self.for_db, category, word, translation)
                print(f"Word '{word} - {translation}' moved to {category} category.")
            else:
                print("Index out of range. Please enter a valid number.")

    def run_dict_ui(self, options: dict) -> None:
        """Generic UI for dictionary display and interaction."""

        choose = [f"{key}. {func.__doc__}" for key, func in options.items()]
        choose[1] = "2. Enter the word to mark as known."
        choose[2] = "3. Enter the word to mark as ignore."
        choose[3] = "4. Enter the word to defer."
        choose = "\n".join(["Menu:", *choose])

        while self.words:
            self.df = pd.DataFrame(self.words.values())
            if not self.known and not self.for_db:
                self.df = self.df.drop(columns=["category"])
            print(self.df.to_string())
            print(choose)

            choice = input("Choose an option: ")
            if action := options.get(choice):
                action()
                if action == self.save_and_exit or action == self.exit_only:
                    return
            else:
                print("Invalid choice. Try again.")

        print("No unknown words left.")
        self.exit_only()

    def show_dict(self) -> None:
        """Display the dictionary (from list) and handle user actions."""

        options = {
            "1": self.sort_words,
            "2": lambda: self.handle_word_action(
                "Enter the word to mark as known", "Known"
            ),
            "3": lambda: self.handle_word_action(
                "Enter the word to mark as ignore", "Ignore"
            ),
            "4": lambda: self.handle_word_action("Enter the word to defer", "Deferred"),
            "5": self.show_known_words,
            "6": self.save_to_separate_file,
            "7": self.save_and_exit,
            "8": self.exit_only,
        }

        self.run_dict_ui(options=options)

    def show_dict_for_db(self) -> None:
        """Display dictionary from DB and handle actions."""

        options = {
            "1": self.sort_words,
            "2": lambda: self.handle_word_action(
                "Enter the word to mark as known", "Known"
            ),
            "3": lambda: self.handle_word_action(
                "Enter the word to mark as ignore", "Ignore"
            ),
            "4": lambda: self.handle_word_action("Enter the word to defer", "Deferred"),
            "5": self.save_and_exit,
            "6": self.exit_only,
        }

        self.run_dict_ui(options=options)

    def run(self) -> None:
        """Run the dictionary application without database interaction."""

        save.create_tables(self.conn)
        if self.for_db:
            self.insert_words()
            if self.check_unknown_words():
                self.show_dict_for_db()
        else:
            self.filter_words()
            print("Dictionary created successfully!")
            if self.check_unknown_words():
                print("Unknown words were found.")
                self.show_dict()

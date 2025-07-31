import pandas as pd
import csv
import shutil
import sqlite3
import os


def clean_up(conn: sqlite3.Connection) -> None:
    """Clean up the database by deleting entries in new_words and deferred_words."""
    with conn:
        conn.execute("DELETE FROM new_words")
        conn.execute("DELETE FROM deferred_words")


def create_tables(conn: sqlite3.Connection) -> None:
    """Create necessary tables in the SQLite database."""
    queries = [
        """
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT,
                translation TEXT,
                pos TEXT,
                count INTEGER,
                category TEXT,
                UNIQUE(word, translation)
            )
            """,
        """
            CREATE TABLE IF NOT EXISTS new_words (
                id INTEGER PRIMARY KEY,
                word TEXT,
                translation TEXT,
                pos TEXT,
                count INTEGER,
                count_in_db INTEGER,
                total_count INTEGER,
                category TEXT
            )
            """,
        """
            CREATE TABLE IF NOT EXISTS deferred_words (
                word TEXT,
                translation TEXT,
                pos TEXT,
                total_count INTEGER
            )
            """,
    ]

    with conn:
        for query in queries:
            conn.execute(query)
    clean_up(conn)


def insert_new_word(conn: sqlite3.Connection, *row) -> None:
    conn.execute(
        "INSERT INTO new_words (word, translation, pos, count, count_in_db, total_count, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
        row,
    )


def move_word(
    conn: sqlite3.Connection, for_db: bool, category: str, word: str, translation: str
) -> None:
    with conn:
        conn.execute(
            """
            UPDATE new_words
            SET category = ?
            WHERE word = ? AND translation = ?
        """,
            (category, word, translation),
        )
        if not for_db and category == "Deferred":
            conn.execute(
                """
                INSERT INTO deferred_words (word, translation, pos, total_count)
                SELECT word, translation, pos, count
                FROM new_words
                WHERE word = ? AND translation = ?
            """,
                (word, translation),
            )
            conn.execute(
                "DELETE FROM new_words WHERE word = ? AND translation = ?",
                (word, translation),
            )


def append_to_csv(data: list, count: int = None) -> None:
    csv_path = "history.csv"
    file_exists = os.path.exists(csv_path)

    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["file", "unknown_words"])
        for entry in data:
            if count is not None:
                writer.writerow([entry, count])
            else:
                writer.writerow(entry)


def save(conn: sqlite3.Connection, files: list) -> None:

    with conn:
        conn.execute(
            """
            INSERT INTO words (word, translation, pos, count, category)
            SELECT word, translation, pos, total_count AS count, category
            FROM new_words
            WHERE TRUE
            ON CONFLICT(word, translation) DO UPDATE SET
                count = excluded.count,
                category = excluded.category,
                pos = excluded.pos
            """
        )

        conn.execute(
            """
            INSERT INTO words (word, translation, pos, count, category)
            SELECT word, translation, pos, total_count AS count, 'Deferred'
            FROM deferred_words
            WHERE TRUE
            ON CONFLICT(word, translation) DO UPDATE SET
                count = excluded.count,
                category = excluded.category,
                pos = excluded.pos
            """
        )

        count = conn.execute(
            """
            SELECT
            (SELECT COUNT(*) FROM new_words WHERE category = 'Unknown') +
            (SELECT COUNT(*) FROM deferred_words)
            """
        ).fetchone()[0]
        append_to_csv(files, count)


def save_for_db(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            """
            UPDATE words
            SET category = new_words.category
            FROM new_words
            WHERE words.id = new_words.id
            AND words.category != new_words.category

        """
        )


def save_to_csv(
    data: dict,
    filename: str,
    headers: list[str] = None,
) -> None:
    if not headers:
        headers = list(next(iter(data)).keys())
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def show_history(csv_path="history.csv") -> None:
    if not os.path.isfile(csv_path):
        print(f"File {csv_path} doesn't exist.")
        print("Make your dictionary first(-m flag)")
        return

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        print(f"{'File':<40} | {'Unknown Words'}")
        print("-" * 60)
        for row in reader:
            print(f"{row['file']:<40} | {row['unknown_words']}")


def import_dict(path: str) -> None:
    def check_files(folder_path: str) -> dict:
        targets = {
            "database.db": None,
            "history.csv": None,
        }

        for filename in targets.keys():
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                targets[filename] = full_path

        for filename in targets:
            if targets[filename] is None:
                name_part, ext = filename.split(
                    "."
                )  # 'database', 'db' або 'history', 'csv'
                for f in os.listdir(folder_path):
                    if name_part in f.lower() and f.lower().endswith(f".{ext}"):
                        targets[filename] = os.path.join(folder_path, f)
                        break
        return targets

    def import_dict(path) -> None:
        create_tables()
        conn = sqlite3.connect("database.db")
        with conn:
            conn.execute(
                f"""ATTACH DATABASE ? AS db_a;
                INSERT INTO words (word, translation, pos, count, category)
                SELECT word, translation, pos, count, category FROM db_a.words
                WHERE TRUE
                ON CONFLICT(word, translation) DO UPDATE SET
                    count = count + excluded.count;
                DETACH DATABASE db_a;
                """,
                (path,),
            )

    def import_csv(source_file: str) -> None:
        with open(source_file, mode="r", encoding="utf-8", newline="") as src_file:
            reader = csv.reader(src_file)
        append_to_csv(reader)

    targets = check_files(path)
    db, history = targets.values()
    if history and not db:
        print("No db but history")
        return
    if db:
        import_dict(db)
    if history:
        import_csv(history)


def export_dict(path: str) -> None:
    new_path = f"{path}/dictaker_backup"
    os.makedirs(new_path, exist_ok=True)
    shutil.copy("database.db", new_path)
    shutil.copy("history.csv", new_path)


def save_xlsx(data: list, name: str) -> None:
    pd.DataFrame(data, columns=["Word", "Count"])
    with pd.ExcelWriter(name, engine="openpyxl", mode="a") as writer:
        data.to_excel(writer, sheet_name="Words", index=False)

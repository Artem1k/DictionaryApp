# Dictaker

Dictaker is a command-line tool that helps you build a personalized English dictionary by analyzing subtitle files (in `.xlsx` format) downloaded using the [Language Reactor](https://www.languagereactor.com/) browser extension.
It processes subtitle data to identify unknown words and provides detailed information to help you learn and manage your vocabulary effectively.

## Installation

```bash
# Clone the repository
git clone https://github.com/Artem1k/DictionaryApp.git
cd dictaker

# Use your preferred tool to create virtual environment

# Install via pip from source
pip install .

# Run the CLI tool
dictaker --help
# Or
dictaker
```

---

## How it works

1. The program reads `.xlsx` subtitle files exported via Language Reactor.
2. Extracts unknown or deferred words.
3. Displays words with detailed information.
4. Lets you interactively manage your vocabulary (mark as known, ignore, defer, etc.).
5. Saves words to a persistent SQLite database, which can be viewed, managed, imported, and exported.

---

## Features

- [🚀 Make dictionary (`make_dict`)](#-feature-make_dict)
- [📖 View your personal dictionary (`show_dict`)](#-feature-show_dict)
- [🕘 Show history(processed files)](#-feature-show-history)
- [📥 Import dictionary](#-feature-import)
- [📤 Export dictionary](#-feature-export)
- [🌐 Change target language](#-feature-change-target-language)

---

### 🚀 Feature: make_dict

This command analyzes `.xlsx` subtitle files — either a single file, multiple files separated by spaces, or an entire folder. It counts the subtitles, identifies unknown or deferred words, and displays word details:

- Word  
- Translation  
- Part of speech (POS)  
- Frequency in the subtitles  
- Frequency already recorded in the database  
- Total combined frequency

#### Options available:

- Sort by `word`, `pos`, `count`, `count_in_db`, `total_count`, `category` (ascending or descending).
- Mark words as:
  - Known  
  - Ignore  
  - Defer (temporarily skip during current session)
- Toggle display of known words that appear in subtitles. The category will show up when known words are showing.
- Save word lists to separate files.
- Save and exit.
- Exit without saving.

> 💡 **Tip:** You can use multiple indexes or index ranges when marking words. Example: `1 2 3-5 9-6`.

---

### 📖 Feature: show_dict

View your personal dictionary and continue marking words as known, ignored, or deferred.
Unlike in `make_dict`, ignored and deferred words still appear in this session view.

This command shows:

- Word itself  
- Translation  
- Part of speech (POS)  
- Frequency already recorded in the database  
- Category

#### Options for personal dict

- Sort by `id`, `word`, `pos`, `count`, `category` (ascending or descending).
- Mark words as:
  - Known  
  - Ignore  
  - Defer (you can treat this as "Unknown")
- Save and exit.
- Exit without saving.

> 💡 **Tip:** Index ranges work here too — e.g., 1 2 3-5.

---

### 🕘 Feature: show history

Showing the history of processed `.csv` files and the number of unknown words found in each.
Words are saved with a unique ID in the database, so to review the added words, use [show_dict](#-feature-show_dict).

---

### 📥 Feature: import

Imports a dictionary from a `.csv` file.
If a word already exists, its count is increased accordingly.

---

### 📤 Feature: export

Exports your current dictionary to a `.csv` file - just provide the path to the folder.

---

### 🌐 Feature: Change target language

Run this command without arguments to see available language options.

---

## 🔎 How Words Are Processed

This project uses the `spaCy` library and the `en_core_web_md` model.
It’s fast and lightweight but not always accurate in part-of-speech (POS) tagging.
Words with a named entity type (`ent_type`), such as names of people or places, are excluded automatically. However, this isn’t always reliable, so the Ignore category allows you to manually clean up such entries.

Translations use `GoogleTranslator`. Some modal verbs like "can" or "should" may not translate properly — especially to Ukrainian — maybe because translation is done out of context.

Future versions may use better models or APIs to improve accuracy.

---

## 🛠️ To Do

- Add built-in learning tools
- GUI
- Browser extension (maybe)

---

## 🤝 Contribution

Contributions are welcome! Feel free to fork, create pull requests, or report issues.

---

## 📝 License

Licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

import argparse
from dictaker import make, extractor, save


def menu():
    print("Welcome to the Dictaker!")
    menu = {
        "0": extractor.set_lang,
        "1": make.make,
        "2": make.show_dict,
        "3": save.show_history,
        "4": lambda: save.import_dict(path=input("Enter the path to the files: ")),
        "5": lambda: save.export_dict(path=input("Enter the path to export: ")),
        "6": lambda: print("Goodbye!"),
    }
    while True:
        choice = input(
            "Menu:\n0. Change target language\n1. Make dict\n2. Show dict\n3. Show history(processed files)\n4. Import dict\n5. Export dict\n6. Exit\nChoose an option: "
        )
        action = menu.get(choice)
        if action:
            action()
            if choice == "6":
                break
        else:
            print("Invalid choice. Try again.\n")


def main():
    parser = argparse.ArgumentParser(description="Dictaker CLI — dictionary tool")

    parser.add_argument(
        "-l",
        "--language",
        metavar="language",
        help="Set (target)language for translation, default is Ukrainian",
    )
    parser.add_argument("-m", "--make", action="store_true", help="Create dictionary")
    parser.add_argument("-s", "--show", action="store_true", help="Show dictionary")
    parser.add_argument(
        "-f", "--files", action="store_true", help="Show history(processed files)"
    )
    parser.add_argument(
        "-i", "--import_", metavar="PATH", help="Import dictionary from PATH"
    )
    parser.add_argument(
        "-e", "--export", metavar="PATH", help="Export dictionary to PATH"
    )

    args = parser.parse_args()

    # Якщо нічого не передано — запусти меню
    if not any(vars(args).values()):
        menu()
        return

    if args.language:
        extractor.set_lang(lang=args.language)
    elif args.make:
        make.make()
    elif args.show:
        make.show_dict()
    elif args.import_:
        save.import_dict(path=args.import_)
    elif args.export:
        save.export_dict(path=args.export)
    elif args.files:
        save.show_history()


if __name__ == "__main__":
    main()

import dictionary


def main():
    print("Welcome to the Dictaker!")
    menu = {
        "1": dictionary.make,
        "2": lambda: dictionary.show_dict(),
        "3": lambda: dictionary.import_dict(path=input("Enter the path to the files: ")),
        "4": lambda: dictionary.export_dict(path=input("Enter the path to export: ")),
        "5": lambda: print("Goodbye!")
    }
    while True:
        choice = input("Choose an option:\n1. Make dict\n2. Show dict\n3. Import dict\n4. Export dict\n5. Exit\n")
        action = menu.get(choice)
        if action:
            action()
            if choice == "5":
                break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

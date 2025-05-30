import dictionary


def main():
    print("Welcome to the Dictaker!")
    while True:
        choice = input("Choose an option:\n1. Make dict\n2. Show dict\n3. Import dict\n4. Export dict\n5. Exit\n")
        match choice:
            case "1":
                dictionary.make()
            case "2":
                print("Showing dictionary...")
                dictionary.show_dict()
            # case "3":
            #     path = input("Enter the path to the files: ")
            #     dictionary.import_dict(path)
            case "4":
                path = input("Enter the path to export: ")
                dictionary.export_dict(path)
            case "5":
                print("Goodbye!")
                break
            case _:
                print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

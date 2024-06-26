from datetime import datetime, timedelta
import re
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number format.")
        super().__init__(value)

    def validate_phone(self, phone_number):
        return bool(re.match(r'^\d{10}$', phone_number))

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None 

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value.lower() == old_phone.lower():
                phone.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if p.value.lower() == phone.lower():
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phone_str = '; '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phone_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming_dates = [(today + timedelta(days=i)).strftime("%d.%m") for i in range(1, 8)]
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday and record.birthday.value[0:5] in upcoming_dates:
                upcoming_birthdays.append(record)

        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter valid user name."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Incomplete command. Please provide necessary arguments."
    return inner

@input_error
def add_contact(args, address_book):
    name, phone, *_ = args
    record = address_book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        address_book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message        
    

@input_error
def change_contact(args, address_book):
    name, phone, *_ = args
    record = address_book.find(name)
    message = "Contact updated: {} - {}".format(name, phone) if record else "Contact not found: {}".format(name)
    if record and phone:
        record.add_phone(phone)
    return message

@input_error
def show_phone(args, address_book):
    name = args[0]
    if name in address_book:
        return "{}'s phone number: {}".format(name, address_book[name])
    else:
        return "Contact not found: {}".format(name)

@input_error
def show_all(args, address_book):
    if address_book:
        return "\n".join(["{} - {}".format(name, phone) for name, phone in address_book.items()])
    else:
        return "No contacts found"

@input_error
def add_birthday(args, address_book):
    name, birthday = args
    if name in address_book:
        address_book[name].add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args, address_book):
    name = args[0]
    if name in address_book:
        if address_book[name].birthday:
            return "{}'s birthday: {}".format(name, address_book[name].birthday)
        else:
            return f"No birthday found for {name}."
    else:
        return f"Contact {name} not found."

@input_error
def birthdays(args, address_book):
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays:\n" + "\n".join(str(record) for record in upcoming_birthdays)
    else:
        return "No upcoming birthdays in the next week."

def parse_input(user_input):
    parts = user_input.split()
    command = parts[0]
    args = parts[1:]
    return command, args

def main():
    contacts = {}
    address_book = AddressBook()
    print("Welcome to the assistant bot! How can I help you?")

    while True:
        user_input = input("> ")
        command, args = parse_input(user_input)

        if command == "hello":
            print("Welcome to the assistant bot! How can I help you?")
        elif command == "add":
            print(add_contact(args, address_book))
        elif command == "change":
            print(change_contact(args, address_book))
        elif command == "phone":
            print(show_phone(args, address_book))
        elif command == "all":
            print(show_all(args, address_book))
        elif command == "close" or command == "exit":
            print("Good bye!")
            break
        elif command == "add_birthday":
            print(add_birthday(args, address_book))
        elif command == "show_birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(birthdays(args, address_book))
        else:
            print("Unknown command: {}".format(command))

if __name__ == "__main__":
    main()

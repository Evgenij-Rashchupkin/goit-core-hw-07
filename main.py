from collections import UserDict
from datetime import datetime, timedelta
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone):
        if not re.fullmatch(r'\d{10}', phone):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(phone)


class Birthday(Field):
    def __init__(self, value):
        # Проверяем формат даты
        try:
            datetime.strptime(value, "%d.%m.%Y")
            self.value = value  # сохраняем строку, если формат верен
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value  # возвращаем строку формата DD.MM.YYYY


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Phone number {phone} not found")

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            try:
                new_phone_obj = Phone(new_phone)
                self.remove_phone(old_phone)
                self.add_phone(new_phone)
            except ValueError as e:
                raise ValueError(f"Failed to edit phone: {e}")
        else:
            raise ValueError(f"Phone number {old_phone} not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        if not self.birthday:
            self.birthday = Birthday(birthday)
        else:
            raise ValueError("Birthday already set")

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Record with name {name} not found")

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now().date()
        week_from_today = today + timedelta(days=7)

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if today <= birthday_this_year <= week_from_today:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                    })

        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "This name does not exist. Input another name."
        except IndexError:
            return "Enter the argument for the command."

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, new_phone = args
    record = book.find(name)
    if record:
        if record.phones:
            record.phones[0] = Phone(new_phone)
        else:
            record.add_phone(new_phone)
        return f"Contact {name} updated successfully."
    else:
        raise KeyError("Contact not found.")


@input_error
def get_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}: {'; '.join(p.value for p in record.phones)}"
    else:
        raise KeyError("Contact not found.")


def all_contacts(book: AddressBook):
    if book:
        return str(book)
    else:
        return "No contacts found."


@input_error
def add_birthday(args, book: AddressBook):
    name, date_str = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."

    try:
        birthday = Birthday(date_str)
        record.birthday = birthday
        return f"Birthday for {name} set to {date_str}."
    except ValueError as e:
        return str(e)


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    else:
        return f"No birthday set for {name}."


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    result = "\n".join([f"{contact['name']}: {contact['birthday']}" for contact in upcoming])
    return result


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(get_phone(args, book))
        elif command == "all":
            print(all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

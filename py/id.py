#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import sqlite3
import typing as t
from pathlib import Path


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Создать таблицу с информацией о должностях.
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS numbers (
        human_id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_numer INTEGER NOT NULL
        )
        """
    )
    # Создать таблицу с информацией о работниках.
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS people (
        human_id INTEGER PRIMARY KEY AUTOINCREMENT,
        human_name TEXT NOT NULL,
        human_bd TEXT NOT NULL,
        FOREIGN KEY(human_id) REFERENCES numbers(human_id)
        )
        """
    )
    conn.close()


def add_human(
        database_path: Path,
        name: str,
        phone: int,
        date_bday: str
) -> None:
    """
    Добавить человека в базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT human_id FROM people WHERE human_name = ?
        """,
        (name,)
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            """
            INSERT INTO people (human_name, human_bd) VALUES (?, ?)
            """,
            (name, date_bday)
        )
        human_id = cursor.lastrowid

    else:
        human_id = row[0]
        # Добавить информацию о новом человеке.
    cursor.execute(
        """
        INSERT INTO numbers (human_id,  phone_numer)
        VALUES (?, ?)
        """,
        (human_id, phone)
    )
    conn.commit()
    conn.close()


def display_human(people: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список работников.
    """
    # Проверить, что список работников не пуст.
    if people:
        # Заголовок таблицы.
        line = "+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4,
            "-" * 30,
            "-" * 15,
            "-" * 15
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^15} | {:^15} |".format(
                "№",
                "Фамилия и имя",
                "День рождения",
                "Телефон"

            )
        )
        print(line)

        # Вывести данные о всех людях.
        for idx, human in enumerate(people, 1):
            print(
                f"| {idx:>4} |"
                f' {human.get("name", ""):<30} |'
                f' {human.get("phone", 0):<15} |'
                f' {human.get("birthday")}      |'
            )
            print(line)

    else:
        print("Список пуст.")


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.human_name, people.human_bd, numbers.phone_numer
        FROM numbers
        INNER JOIN people ON people.human_id = numbers.human_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row[0],
            "phone": row[1],
            "birthday": row[2],
        }
        for row in rows
    ]


def find_human(
        database_path: Path, bd: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Вывод на экран информации о человека по фамилии
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.human_name, people.human_bd, numbers.phone_numer
        FROM numbers
        INNER JOIN people ON people.human_id = numbers.human_id
        WHERE people.human_name LIKE ? || '%'
        """,
        (bd,)
    )
    rows = cursor.fetchall()
    conn.close()
    if len(rows) == 0:
        return []

    return [
        {
            "name": row[0],
            "birthday": row[1],
            "phone": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    """
    Главная функция программы.
    """
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.cwd() / "data_ph.db"),
        help="The database file name"
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("people")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления работника.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new worker"
    )

    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The worker's name"
    )

    add.add_argument(
        "-p",
        "--phone",
        type=int,
        action="store",
        help="The worker's post"
    )

    add.add_argument(
        "-bd",
        "--bday",
        action="store",
        required=True,
        help="The year of hiring"
    )

    # Создать субпарсер для отображения всех людей.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all people"
    )

    # Создать субпарсер для поиска людей по фамилии.
    find = subparsers.add_parser(
        "find",
        parents=[file_parser],
        help="Find the people"
    )

    find.add_argument(
        "-sn",
        "--surname",
        action="store",
        required=True,
        help="Required surname"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)

    match args.command:
        # Добавить челоека.
        case "add":
            add_human(db_path, args.name, args.phone, args.bday)
        # Отобразить всех людей.
        case "display":
            display_human(select_all(db_path))
        # Выбрать требуемых людей
        case "find":
            display_human(find_human(db_path, args.surname))


if __name__ == "__main__":
    main()

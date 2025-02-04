import calendar
import json
import sqlite3
import threading
from datetime import datetime
from sqlite3 import Error

import requests
from requests import exceptions
from rich import print
from rich.panel import Panel

# from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.progress import track


# no tests for this function as it is not called anywhere in the command directly
def createConnection():
    """
    Creates a database connection to a SQLite database VocabularyBuilder.db

    Returns:
        Connection object or None.
    """
    conn = None
    try:
        conn = sqlite3.connect("./VocabularyBuilder.db")
    except Error as e:
        print(e)
    return conn


# no tests for this function as it is not called anywhere in the command directly
def createTables(conn: sqlite3.Connection) -> None:
    """
    1. Creates the tables in the database if they do not exist
    2. Tables created are words, cache_words, collections, quiz_history, quotes, rss
    3. The tables are created using the SQL statements in the docstring with respective column names and data types
    4. The tables are created using the execute method of the connection object
    5. The connection object is passed as an argument to the function

    Args:
        conn (sqlite3.Connection): Connection object
    """

    words = """CREATE TABLE IF NOT EXISTS "words" (
	"word"	TEXT,
	"datetime"	timestamp NOT NULL UNIQUE,
	"tag"	TEXT,
	"mastered"	INTEGER NOT NULL DEFAULT 0,
	"learning"	INTEGER NOT NULL DEFAULT 0,
	"favorite"	INTEGER NOT NULL DEFAULT 0
);
    """

    cache_words = """CREATE TABLE IF NOT EXISTS "cache_words" (
	"word"	TEXT NOT NULL UNIQUE,
    "api_response" json NOT NULL
);
    """

    collections = """CREATE TABLE IF NOT EXISTS "collections" (
            "word"	TEXT NOT NULL,
            "collection" TEXT NOT NULL
            );
        """

    quiz_history = """CREATE TABLE IF NOT EXISTS "quiz_history" (
            "type" TEXT NOT NULL,
            "datetime" timestamp NOT NULL UNIQUE,
            "question_count" INTEGER NOT NULL,
            "points" INTEGER NOT NULL,
            "duration" INTEGER NOT NULL
            );
        """

    quotes = """ CREATE TABLE IF NOT EXISTS "quotes" (
            "quote" TEXT NOT NULL UNIQUE,
            "author" TEXT,
            "datetime" timestamp NOT NULL
            );
            """

    rss = """ CREATE TABLE IF NOT EXISTS "rss" (
            "title" TEXT NOT NULL,
            "link" TEXT NOT NULL UNIQUE,
            "description" TEXT,
            "datetime" timestamp NOT NULL
            );
            """

    try:
        c = conn.cursor()
        c.executescript(
            words + cache_words + collections + quiz_history + quotes + rss
        )  # execute multiple statements
    except Exception as e:
        print(e)


# no tests for this function as it is not called anywhere in the command directly
def initializeDB() -> None:
    """Initializes the database"""

    conn = createConnection()
    createTables(conn)


# NOTE: Use this command very sparingly. It is not recommended to use this command more than once a week due to possible API overuse

# TODO: ADD ASYNCIO MULTITHREADING TO THIS FUNCTION
def refresh_cache() -> None:
    """
    Refreshes the cache of the words in the database.

    1. Connect to the database
    2. Check if the cache is empty, if yes, then do nothing.
    3. If the cache is not empty, then we need to refresh it.
    4. Get all the words from the cache.
    5. For each word, get the response from the API and update the cache.
    6. If there's an error, then show a error message and exit.
    7. If there's no error, then update the cache.
    8. If the cache is updated, then show a success message.
    """

    # check if cache is empty, if yes then do nothing
    conn = createConnection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM cache_words")
    if not c.fetchone()[0]:
        return
    c.execute("SELECT word FROM cache_words")
    rows = c.fetchall()

    total = 0
    for row in rows:
        # ----------------- Progress Bar -----------------#
        for _ in track(range(len(rows)), description=" 🔃 Refreshing Cache "):

            # ----------------- Progress Bar -----------------#

            word = row[0]
            try:
                response = requests.get(
                    f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                )
                response.raise_for_status()

            except exceptions.ConnectionError as error:
                print(
                    Panel(
                        title="[b reverse red]  Error!  [/b reverse red]",
                        title_align="center",
                        padding=(1, 1),
                        renderable="[bold red]Error: You are not connected to the internet.[/bold red] ❌",
                    )
                )
            else:
                if response.status_code == 200:
                    c.execute(
                        "UPDATE cache_words SET api_response=? WHERE word=?",
                        (json.dumps(response.json()[0]), word),
                    )
                    conn.commit()

            # update the progress bar
            total += 1

    print(
        Panel(
            title="[b reverse green]  Success!  [/b reverse green]",
            title_align="center",
            padding=(1, 1),
            renderable="Cache refreshed successfully. ✅",
        )
    )

import sqlite3
import os
from pathlib import Path


APP_NAME = "alexandria"
DB_NAME = "alexandria.db"


def build_database_path():
    home = Path.home()

    if os.name == "nt":
        app_dir = home / 'AppData' / APP_NAME
    else:
        app_dir = home / '.local' / APP_NAME

    app_dir.mkdir(parents=True, exist_ok=True)

    full_db_path = app_dir / DB_NAME

    return str(full_db_path)


DB_PATH = build_database_path()


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def create_tables():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            url TEXT NOT NULL,
            tags TEXT,
            description TEXT,
            created_at TEXT DEFAULT (date('now', 'localtime'))
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reading_progress (
            book_id INTEGER PRIMARY KEY,
            chapter INTEGER,
            page INTEGER,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        )
        """)


def find_duplicate_book(conn, title, author):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM books
        WHERE title = ? COLLATE NOCASE
        AND author = ? COLLATE NOCASE
                   """, (title, author))

    return cursor.fetchone()


def insert_book(title, author, url, tags, description):
    with connect_db() as conn:
        duplicate = find_duplicate_book(conn, title, author)
        if duplicate:
            return { "success": False, "message": "Livro já esta armazenado", "duplicate": True }
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO books (title, author, url, tags, description)
            VALUES (?, ?, ?, ?, ?)   
        """, (title, author, url, tags, description))

    return { "success": True, "message": f"'{title}' por '{author}' salvo com sucesso" }


def fetch_all_books():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY created_at DESC")

        return [dict(row) for row in cursor.fetchall()]


def remove_book(book_id: int):
    with connect_db() as conn:
        cursor = conn.cursor()  
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        affected = cursor.rowcount
    
    if affected == 0:
        return { "success": False, "message": "Livro não encontrado" }

    return { "success": True, "message": "Livro deletado com sucesso" }


def fetch_book(book_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        result = cursor.fetchone()

        return dict(result) if result else None


def modify_book(book_id, title, author, url, tags, description):
    with connect_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))

        if not cursor.fetchone():
            return { "success": False, "message": "Livro não encontrado" }
        
        updates = []
        values = []
        
        if title is not None:
            updates.append("title = ?")
            values.append(title)
        if author is not None:
            updates.append("author = ?")
            values.append(author)
        if url is not None:
            updates.append("url = ?")
            values.append(url)
        if tags is not None:
            updates.append("tags = ?")
            values.append(tags)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        
        if updates:
            values.append(book_id)
            query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(values))
        
        return { "success": True, "message": f"Livro atualizado com sucesso" }


def update_reading_progress(book_id, chapter, page):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reading_progress (book_id, chapter, page)
            VALUES (?, ?, ?)
            ON CONFLICT(book_id) DO UPDATE SET
                chapter = excluded.chapter,
                page = excluded.page;
        """, (book_id, chapter, page))

        return { "success": True, "message": "Progresso atualizado" }


def get_reading_progress(book_id):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT chapter, page
        FROM reading_progress
        WHERE book_id = ?
        """, (book_id,))

        return cursor.fetchone()

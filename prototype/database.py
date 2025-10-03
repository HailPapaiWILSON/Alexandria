import sqlite3

DB_NAME: str = "alexandria.db"

def get_db_connection() -> sqlite3.Connection:
    conn: sqlite3.Connection = sqlite3.connect(DB_NAME)
    return conn

def create_tables() -> None:
    conn: sqlite3.Connection = get_db_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TEXT DEFAULT (date('now', 'localtime'))
        )
        """)

def add_book(title: str, author: str, url: str) -> None:
    conn: sqlite3.Connection = get_db_connection()
    with conn:
        conn.execute("""
        INSERT INTO books (title, author, url)
        VALUES (?, ?, ?)
        """, (title, author, url))
    conn.close()
    print(f"\t✅ Added '{title}' by {author} to your library.")

def book_count() -> int:
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    count: int = cursor.fetchone()[0]
    conn.close()
    return count

def list_books() -> list[tuple]:
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
    books: list[tuple] = cursor.fetchall()  # returns tuples: (id, title, author, url, created_at)
    conn.close()
    return books

def delete_book(book_id: int) -> None: 
    conn: sqlite3.Connection = get_db_connection()
    with conn:
        cur: sqlite3.Cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        affected: int = cur.rowcount
    conn.close()
    if affected == 0:
        print("\tBook not found.")
    else:
        print(f"\t✅ Deleted book with ID {book_id} from your library.")

def open_book(book_id: int) -> str | None:
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    cursor.execute("SELECT url FROM books WHERE id = ?", (book_id,))
    result: tuple | None = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def search_books(term: str) -> list[tuple]:
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    search_term: str = f"%{term}%"
    cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? COLLATE NOCASE
        OR author LIKE ? COLLATE NOCASE
    """, (search_term, search_term))
    books: list[tuple] = cursor.fetchall()
    conn.close()
    return books
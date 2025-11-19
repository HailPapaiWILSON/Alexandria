import sqlite3
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

APP_NAME = "alexandria"
DB_NAME = "alexandria.db"

def build_database_path():
    if os.name == "nt":
        app_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', APP_NAME)
    else:
        app_dir = os.path.join(os.path.expanduser('~'), '.config', APP_NAME)

    os.makedirs(app_dir, exist_ok=True)
    full_db_path = os.path.join(app_dir, DB_NAME)
    return full_db_path

DB_PATH = build_database_path()

def connect_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao conectar ao banco de dados: {e}[/bold red]"))
        raise

def create_tables():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (date('now', 'localtime'))
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_tags (
            book_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (book_id, tag_id),
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        """)

def find_existing_book(conn, title, author):
    """Check for duplicates using existing connection"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM books
            WHERE title = ? COLLATE NOCASE
            AND author = ? COLLATE NOCASE
                       """, (title, author))
        return cursor.fetchone()
    except sqlite3.Error as e:
        raise Exception(f"Erro ao verificar livros repetidos: {e}")

def insert_book(title, author, url, tags, description):
    try:
        with connect_db() as conn:
            # Check duplicates within the same connection
            duplicate = find_existing_book(conn, title, author)
            if duplicate:
                return {
                    "success": False,
                    "message": "Livro já esta armazenado",
                    "duplicate": True,
                    "book_id": duplicate['id']
                }
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books (title, author, url, description)
                VALUES (?, ?, ?, ?)   
            """, (title, author, url, description))
            book_id = cursor.lastrowid

            if tags:
                for tag in tags:
                    if tag.strip():
                        tag_id = ensure_tag(conn, tag)
                        cursor.execute("INSERT INTO book_tags (book_id, tag_id) VALUES (?, ?)", (book_id, tag_id))
    
        return {
            "success": True,
            "message": f"'{title}' por '{author}' salvo com sucesso",
            "book_id": book_id
        }
    except sqlite3.Error as e:
        return {
            "success": False,
            "message": f"Erro ao adicionar livro: {e}"
        }

def fetch_tags_for(book_id):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.name
                FROM tags t
                JOIN book_tags bt ON t.id = bt.tag_id
                WHERE bt.book_id = ?
                ORDER by t.name
            """, (book_id,))
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise Exception(f"Erro ao buscar tags do livro {book_id}: {e}")

def count_books():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            return cursor.fetchone()[0]
    except sqlite3.Error as e:
        raise Exception(f"Erro ao contar livros: {e}")
              
def fetch_all_books():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
            books = [dict(row) for row in cursor.fetchall()]

            for book in books:
                book['tags'] = fetch_tags_for(book['id'])
            return books
    except sqlite3.Error as e:
        raise Exception(f"Erro ao listar livros: {e}")
    
def remove_book(book_id: int):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()  
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            affected = cursor.rowcount
        
        if affected == 0:
            return {
                "success": False,
                "message": "Livro não encontrado"
            }
        else:
            return {
                "success": True,
                "message": "Livro deletado com sucesso"
            }
    except sqlite3.Error as e:
        return {
        "success": False, 
        "message": f"Erro ao deletar livro: {e}"}

def search_books(term: str, search_type="all"):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            search_term = f"%{term}%"
            
            if search_type == "title":
                cursor.execute("SELECT * FROM books WHERE title LIKE ? COLLATE NOCASE", (search_term,))
            
            elif search_type == "author":
                cursor.execute("SELECT * FROM books WHERE author LIKE ? COLLATE NOCASE", (search_term,))
                
            elif search_type == "tag":
                cursor.execute("""
                    SELECT DISTINCT b.*
                    FROM books b
                    JOIN book_tags bt ON b.id = bt.book_id
                    JOIN tags t ON bt.tag_id = t.id
                    WHERE t.name LIKE ? COLLATE NOCASE
                """, (search_term,))
            else:
                cursor.execute("""
                    SELECT DISTINCT b.*
                    FROM books b
                    LEFT JOIN book_tags bt ON b.id = bt.book_id
                    LEFT JOIN tags t ON bt.tag_id = t.id
                    WHERE b.title LIKE ? COLLATE NOCASE
                    OR b.author LIKE ? COLLATE NOCASE
                    OR t.name LIKE ? COLLATE NOCASE
                """, (search_term, search_term, search_term))
            
            books = [dict(row) for row in cursor.fetchall()]
            
            for book in books:
                book['tags'] = fetch_tags_for(book['id'])
            
            return books
    except sqlite3.Error as e:
        raise Exception(f"Erro ao pesquisar livros: {e}")

def fetch_book(book_id):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()
            
            if result:
                book = dict(result)
                book['tags'] = fetch_tags_for(book_id)
                return book
            return None
    except sqlite3.Error as e:
        raise Exception(f"Erro ao buscar detalhes do livro: {e}")

def ensure_tag(conn, tag_name):
    cursor = conn.cursor()
    tag_name = tag_name.strip().lower()

    cursor.execute("SELECT id FROM tags WHERE name = ? COLLATE NOCASE", (tag_name,))
    result = cursor.fetchone()

    if result:
        return result['id']

    cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
    return cursor.lastrowid

def modify_book(book_id, title, author, url, tags, description):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            
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
            if description is not None:
                updates.append("description = ?")
                values.append(description)
            
            if updates:
                values.append(book_id)
                query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, tuple(values))
            
            if tags is not None:
                cursor.execute("DELETE FROM book_tags WHERE book_id = ?", (book_id,))
                
                for tag in tags:
                    if tag.strip():
                        tag_id = ensure_tag(conn, tag)
                        cursor.execute("""
                            INSERT INTO book_tags (book_id, tag_id)
                            VALUES (?, ?)
                        """, (book_id, tag_id))
            
            affected = cursor.rowcount if not updates else 1
            
            if affected == 0 and not tags:
                return {
                    "success": False,
                    "message": "Livro não encontrado"
                }
            else:
                return {
                    "success": True,
                    "message": f"{book_id} atualizado com sucesso"
                }
                
    except sqlite3.Error as e:
        return {
            "success": False,
            "message": f"Erro ao atualizar livro: {e}"
        }

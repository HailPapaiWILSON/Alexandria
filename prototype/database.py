import sqlite3
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

APP_NAME = "alexandria"
DB_NAME = "alexandria.db"

def get_path():
    if os.name == "nt":
        app_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', APP_NAME)
    else:
        app_dir = os.path.join(os.path.expanduser('~'), '.config', APP_NAME)

    os.makedirs(app_dir, exist_ok = True)

    full_db_path = os.path.join(app_dir, DB_NAME)

    return full_db_path

DB_PATH = get_path()

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao connectar ao banco de dados: {e}[/bold red]"))
        raise

def create_tables():
    conn = get_db_connection()
    with conn:
        conn.execute("""
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

def check_duplicates(title, author):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM books
                WHERE title = ? COLLATE NOCASE
                AND author = ? COLLATE NOCASE
                           """, (title, author))
        return cursor.fetchone()
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao verificar duplicatas: {e}[/bold red]"))
        return None

def add_book(title, author, url, tags, description):
    try:
        duplicate = check_duplicates(title, author)
        if duplicate:
            console.print(Panel("[bold yellow] Livro já existe![/bold yellow]"))
            return False
        
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO books (title, author, url, tags, description)
                VALUES (?, ?, ?, ?, ?)   
            """, (title, author, url, tags, description))
        
        console.print(Panel(f"[bold blue]' {title}'[/bold blue] por [bold]{author}[/bold] [green]adicionado![/green]"))
        return True
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao adicionar livro: {e}[/bold red]"))
        return False

def book_count():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao conttar livros: {e}[/bold red]"))
        return 0

def list_books():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
            return cursor.fetchall()
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao listar livros: {e}[/bold red]"))
        return []

def delete_book(book_id: int): 
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()  
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            affected = cursor.rowcount
        
        if affected == 0:
            console.print(Panel("[yellow] Livro não encontrado.[/yellow]"))
            return False
        else:
            console.print(Panel(f"[bold red] Livro com ID {book_id} removido da sua biblioteca.[/bold red]"))
            return True
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao remover livros: {e}[/bold red]"))
        return False

def open_book(book_id: int) -> str | None:
    try:
        conn = get_db_connection()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()

        if result:
            return result['url']
        return None
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao buscar URL para livro (ID {book_id}): {e}[/bold red]"))
        return None

def search_books(term: str, search_type = "all"):
    
    try:
        with get_db_connection() as conn:
            cursor: sqlite3.Cursor = conn.cursor()
            search_term: str = f"%{term}%"
            
            if search_type == "title":
                cursor.execute("SELECT * FROM books WHERE title LIKE ? COLLATE NOCASE", (search_term,))
            
            elif search_type == "author":
                cursor.execute("SELECT * FROM books WHERE author LIKE ? COLLATE NOCASE", (search_term,))
                
            elif search_type == "tag":
                cursor.execute("SELECT * FROM books WHERE tag LIKE ? COLLATE NOCASE", (search_term,))
            else:
                cursor.execute("""
                SELECT * FROM books
                WHERE title LIKE ? COLLATE NOCASE
                OR author LIKE ? COLLATE NOCASE
                OR tags LIKE ? COLLATE NOCASE
            """, (search_term, search_term, search_term))
            books = cursor.fetchall()
        return books
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao buscar livros ('{term}', type: {search_type}): {e}[/bold red]"))
        return []

def update(book_id, title, author, url, tags, description):
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            update = []
            values = []

            if title is not None:
                update.append("title = ?")
                values.append(title)
            if author is not None:
                update.append("author = ?")
                values.append(author)
            if url is not None:
                update.append("url = ?")
                values.append(url)
            if tags is not None:
                update.append("tags = ?")
                values.append(tags)
            if description is not None:
                update.append("description = ?")
                values.append(description)
                
            if not update:
                console.print(Panel(f"[yellow] Nenhum campo para atualizar.[/yellow]"))
                return

            values.append(book_id)
            query = f"UPDATE books SET {','.join(update)} WHERE id = ?"

            cursor.execute(query, tuple(values))
            affected = cursor.rowcount

            conn.close()

            if affected == 0:
                console.print(Panel(f"[yellow] Livro nao encontrado[/yellow]"))
            else:
                console.print(Panel(f" Livro ID - {book_id} [green]atualizado com successo[/green]"))
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao atualizar livro (ID {book_id}): {e}[/bold red]"))
        return False

def get_book_details(book_id):
    try:
        with get_db_connection() as conn:
            cursor= conn.cursor()
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()
        if result:
            return result
        else:
            console.print(Panel(f"[yellow]Detalhes para livro com ID {book_id} não encontrados.[/yellow]"))
            return None
    except sqlite3.Error as e:
        console.print(Panel(f"[bold red] Erro ao buscar detalhes para livro (ID {book_id}): {e}[/bold red]"))
        return None

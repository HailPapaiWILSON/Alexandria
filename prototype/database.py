# Importa o módulo sqlite3 para trabalhar com bancos de dados SQLite
import sqlite3
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

# Nome do arquivo do banco de dados SQLite
APP_NAME: str = "alexandria"
DB_NAME: str = "alexandria.db"

def get_path() -> str:
    if os.name == "nt":
        app_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', APP_NAME)
    else:
        app_dir = os.path.join(os.path.expanduser('~'), '.config', APP_NAME)

    os.makedirs(app_dir, exist_ok = True)

    full_db_path = os.path.join(app_dir, DB_NAME)

    return full_db_path

DB_PATH = get_path()

def get_db_connection() -> sqlite3.Connection:
    """
    Estabelece e retorna uma conexão com o banco de dados SQLite.
    
    Returns:
        sqlite3.Connection: Objeto de conexão com o banco de dados
    """
    conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
    return conn

def create_tables() -> None:
    """
    Cria a tabela 'books' no banco de dados se ela não existir.
    A tabela armazena as seguintes informações:
    - id: Identificador único do livro (gerado automaticamente)
    - title: Título do livro (obrigatório)
    - author: Autor do livro (obrigatório)
    - url: URL do livro (obrigatória)
    - created_at: Data de criação (preenchida automaticamente)
    """
    conn: sqlite3.Connection = get_db_connection()
    with conn:  # Usa o gerenciador de contexto para garantir o commit/rollback
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

def add_book(title: str, author: str, url: str, tags, description) -> None:
    """
    Adiciona um novo livro ao banco de dados.
    
    Args:
        title (str): Título do livro
        author (str): Nome do autor
        url (str): URL do livro
        
    Nota: Usa parâmetros nomeados (?) para prevenir injeção de SQL
    """
    conn: sqlite3.Connection = get_db_connection()
    with conn:  # Garante que as alterações serão salvas (commit) ao final do bloco
        conn.execute("""
        INSERT INTO books (title, author, url, tags, description)
        VALUES (?, ?, ?, ?, ?)   
        """, (title, author, url, tags, description))  
    conn.close()
    console.print(Panel(f"[bold blue] '{title}'[/bold blue] por [bold]{author}[/bold] [green]adicionado com sucesso![/green]"))

def book_count() -> int:
    """
    Conta quantos livros existem no banco de dados.
    
    Returns:
        int: Número total de livros na biblioteca
    """
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")  # Conta todos os registros
    count: int = cursor.fetchone()[0]  # Pega o primeiro resultado da primeira coluna
    conn.close()
    return count

def list_books() -> list[tuple]:
    """
    Lista todos os livros do banco de dados, ordenados do mais recente para o mais antigo.
    
    Returns:
        list[tuple]: Lista de tuplas, onde cada tupla contém:
                    (id, title, author, url, created_at)
    """
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    # Ordena por data de criação em ordem decrescente (mais recente primeiro)
    cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
    books: list[tuple] = cursor.fetchall()  # Retorna todos os registros
    conn.close()
    return books

def delete_book(book_id: int) -> None: 
    """
    Remove um livro do banco de dados com base no ID.
    
    Args:
        book_id (int): ID do livro a ser removido
        
    Nota: Verifica se o livro foi encontrado e removido com sucesso
    """
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    with conn:  # Usa transação para garantir a integridade dos dados
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        affected: int = cursor.rowcount  # Conta quantas linhas foram afetadas
    conn.close()
    
    # Feedback para o usuário
    if affected == 0:
        console.print(Panel("[yellow] Livro não encontrado.[/yellow]"))
    else:
        console.print(Panel(f"[bold red] Livro com ID {book_id} removido da sua biblioteca.[/bold red]"))

def open_book(book_id: int) -> str | None:
    """
    Busca a URL de um livro específico no banco de dados.
    
    Args:
        book_id (int): ID do livro desejado
        
    Returns:
        str | None: URL do livro se encontrado, None caso contrário
    """
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    # Busca apenas a URL do livro com o ID especificado
    cursor.execute("SELECT url FROM books WHERE id = ?", (book_id,))
    result: tuple | None = cursor.fetchone()  # Pega a primeira linha do resultado
    conn.close()
    
    # Retorna a URL se encontrou o livro, senão retorna None
    if result:
        return result[0]  # Retorna o primeiro (e único) campo da tupla (a URL)
    return None

def search_books(term: str, search_type = "all") -> list[tuple]:
    """
    Busca livros por um termo no título ou autor (case insensitive).
    
    Args:
        term (str): Termo de busca (pode ser parte do título ou autor)
        
    Returns:
        list[tuple]: Lista de tuplas contendo os livros encontrados
        
    Nota: A busca é feita usando LIKE com curingas (%) e COLLATE NOCASE para
    ignorar diferenças entre maiúsculas e minúsculas
    """
    conn: sqlite3.Connection = get_db_connection()
    cursor: sqlite3.Cursor = conn.cursor()
    # Adiciona os caracteres curinga para busca parcial
    search_term: str = f"%{term}%"
    
    # Busca em título OU autor, ignorando maiúsculas/minúsculas
    if search_type == "title":
        cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? COLLATE NOCASE
    """, (search_term,))
    
    elif search_type == "author":
            cursor.execute("""
            SELECT * FROM books
            WHERE title LIKE ? COLLATE NOCASE
        """, (search_term,))
        
    elif search_type == "tag":
                cursor.execute("""
                SELECT * FROM books
                WHERE title LIKE ? COLLATE NOCASE
            """, (search_term,))
    else:
        cursor.execute("""
        SELECT * FROM books
        WHERE title LIKE ? COLLATE NOCASE
        OR author LIKE ? COLLATE NOCASE
        OR tags LIKE ? COLLATE NOCASE
    """, (search_term, search_term, search_term))  # Usa o mesmo termo para título e autor
    
    books: list[tuple] = cursor.fetchall()  # Pega todos os resultados que correspondem ao termo de busca
    conn.close()
    return books

def update(book_id, title, author, url, tags, description):
    conn = get_db_connection()
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
        conn.close()
        return

    values.append(book_id)
    query = f"UPDATE books SET {','.join(update)} WHERE id = ?"

    with conn:
        cursor.execute(query, tuple(values))
        affected = cursor.rowcount

    conn.close()

    if affected == 0:
        console.print(Panel(f"[yellow] Livro nao encontrado[/yellow]"))
    else:
        console.print(Panel(f" Livro ID - {book_id} [green]atualizado com successo[/green]"))

def get_book_details(book_id):
    conn = get_db_connection()
    cursor= conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    result = cursor.fetchone()
    conn.close()
    return result

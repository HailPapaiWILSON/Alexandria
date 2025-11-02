import webbrowser
import database
import click
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

console = Console()

@click.group()
def cli():
    database.create_tables()

def create_rich_table(books, title):
    table = Table(
        title = title,
        show_header = True,
        header_style = "bold cyan",
        title_style = "bold blue",
        show_lines = True,
        border_style = "blue",
        padding = (0, 2)
    )

    table.add_column("ID", style="white", width = 4, justify = "center")
    table.add_column("Titulo", style="white", width = 30, justify = "center")
    table.add_column("Autor", style="green", width = 17, justify = "center")
    table.add_column("Tags", style="yellow", width = 17, justify = "center")
    table.add_column("Adicionado em", style="cyan", width = 12, justify = "center")
        
    for book in books:
        book_id: int = book['id']
        title: str = book['title']
        author: str = book['author']
        tags: str = book['tags']
        created_at: str = book['created_at']

        title_text = Text(title)
        title_text.truncate(30, overflow = "ellipsis")

        author_text = Text(author)
        author_text.truncate(17, overflow = "ellipsis")

        tags_text = Text(tags)
        tags_text.truncate(17, overflow = "ellipsis")

        table.add_row(
            str(book_id),
            title_text,
            author_text,
            tags_text,
            created_at
        )
    return table

@cli.command(help = "Adiciona um novo livro (título, autor, URL) à biblioteca.")
def add():
    name = Prompt.ask("[bold white] Nome do livro[/bold white]")
    author = Prompt.ask("[bold white] Autor[/bold white]")
    url = Prompt.ask("[bold white] URL[/bold white]")
    tags = Prompt.ask("[bold white] Tags[/bold white]")
    description = Prompt.ask("[bold white] Descrição[/bold white]")
    
    if not name or not author or not url:
        console.print(Panel("[bold red] Por favor, insira um nome, autor e URL válidos.[/bold red]"))
        return

    description = description if description.strip() else None
    tags = tags if tags.strip() else None
    
    database.add_book(name, author, url, tags, description)

@cli.command(name = "list", help = "Lista todos os livros na biblioteca.")
def list_books():
    total_books = database.book_count()
    if total_books == 0:
        console.print(Panel("[yellow] Sua biblioteca está vazia.[/yellow]"))
        return False
    
    books = database.list_books()
    table_title = "B I B L I O T E C A"
    table = create_rich_table(books, table_title)
    console.print(table)
    
    return True

@cli.command(name = "read", help = "Abre a URL de um livro no navegador usando seu ID.")
@click.argument("book_id", type = int)
def open(book_id):
    url = database.open_book(book_id)
    if url:
        console.print(Panel(f"[green] Abrindo livro ID {book_id}...[/green]"))
        webbrowser.open(url)
    else:
        console.print(Panel("[bold red] Livro não encontrado.[/bold red]"))

@cli.command(name = "delete", help = "Deleta um livro da biblioteca usando seu ID.")
@click.argument("book_id", type = int)
@click.option('--force', '-f', is_flag = True, help = 'Deleta sem confirmação')
def delete(book_id: int, force: bool):
    if not force:
        if click.confirm(f"Tem certeza que deseja deletar livro com ID - {book_id}"):
            database.delete_book(book_id)
    else:   
        database.delete_book(book_id)

@cli.command(name = "search" ,help = "Busca livros por um termo no título ou autor(Case Insensitive).")
@click.argument("term", type = str)
@click.option("--title", "-t", is_flag = True, help = "Busca apenas no título")
@click.option("--author", "-a", is_flag = True, help = "Busca apenas no autor")
@click.option("--tag", "-g", is_flag = True, help = "Busca apenas nas tags")
def search(term, title, author, tag):

    if title:
        search_type = "title"
        search_label = "TÍTULO"
    elif author:
        search_type = "author"
        search_label = "AUTOR"
    elif tag:
        search_type = "tag"
        search_label = "TAGS"
    else:
        search_type = "all"
        search_label = "TODOS OS CAMPOS"

    books = database.search_books(term, search_type)

    if not books:
        console.print(Panel(f"[yellow] Nenhum livro encontrado para [bold white]'{term}'[/bold white][/yellow]"))
        return
    
    table_title = f"RESULTADOS DE BUSCA POR {term} - ({len(books)})"
    table = create_rich_table(books, table_title)
    
    console.print(table)

@cli.command(help = "Atualiza informaçoes de um livros existente.")
@click.argument("book_id", type = int)
@click.option("--title", "-t", help = "Novo Titulo")
@click.option("--author", "-a", help = "Novo Autor")
@click.option("--url", "-u", help = "Novo URL")
@click.option("--tags", "-g", help = "Novas Tags (separadas por vírgula)")
@click.option("--description", "-d", help = "Nova Descrição")
def edit(book_id, title, author, url, tags, description):
    if not any([title, author, url, tags, description]):
        console.print(Panel(f"[bold red] Forneça pelo menos algum campo para atualizar (--title, --author, --url, --tags, --description)[/bold red]"))
        return
    database.update(book_id, title, author, url, tags, description)

@cli.command(help = "Mostra informações detalhadas de um livro.")
@click.argument("book_id", type = int)
def detail(book_id):
    book = database.get_book_details(book_id)

    if not book:
        console.print(Panel(f" [bold red]Livro não encontrado[/bold red]"))
        return

    book_id = book['id']
    title = book['title']
    author = book['author']
    url = book['url']
    tags = book['tags']
    description = book['description']
    created_at = book['created_at']

    info_text = f"""[bold cyan]Titulo:[/bold cyan] [bold white]{title}[/bold white]
[bold cyan]Autor:[/bold cyan]  [bold white]{author}[/bold white]
[bold cyan]URL:[/bold cyan]  [bold white]{url}[/bold white]
[bold cyan]Tags:[/bold cyan]  [bold white]{tags or "Sem tags"}[/bold white]
[bold cyan]Descrição:[/bold cyan]  [bold white]{description or "Nenhuma descrição"}[/bold white]
[bold cyan]Adicionado em:[/bold cyan]  [bold white]{created_at}[/bold white]"""
    
    console.print(Panel(
        info_text, 
        title = f"[bold]ID - {book_id}[/bold]", 
        border_style = "blue",
        padding = (1, 2)
    ))
def main():
    cli()
if __name__ == "__main__":
    main()

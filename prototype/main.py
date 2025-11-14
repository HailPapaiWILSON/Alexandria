import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import rich.box

import database

console = Console()

@click.group()
def cli() -> None:
    database.create_tables()

def create_rich_table(books: list[dict[str, str | int | list[str]]], table_title: str) -> Table:
    table = Table(
        title = table_title,
        show_header = True,
        header_style = "bold cyan",
        title_style = "bold blue",
        show_lines = True,
        border_style = "blue",
        padding = (0, 1),
        box = rich.box.ROUNDED
    )

    table.add_column("ID", style="white", justify="center", no_wrap=True)
    table.add_column("Titulo", style="white", justify="left", overflow="fold")
    table.add_column("Autor", style="green", justify="left", overflow="ellipsis")
    table.add_column("Tags", style="yellow", justify="left", overflow="ellipsis")
    table.add_column("Data", style="cyan", justify="center", no_wrap=True)

    for book in books:
        book_id: int = book["id"]
        title: str = book["title"]
        author: str = book["author"]
        url: str = book["url"]
        tags: list[str] = book["tags"]
        created_at: str = book["created_at"]

        hyperlink: str = f"\033]8;;{url}\033\\{title}\033]8;;\033\\"

        title_text: Text = Text.from_ansi(hyperlink)

        tags_str: str = ", ".join(tags) if tags else "Sem Tags"
        tags_text: Text = Text(tags_str)

        table.add_row(str(book_id), title_text, author, tags_text, created_at)
    return table

@cli.command(help="Adiciona um novo livro (título, autor, URL) à biblioteca.")
def add():
    name = Prompt.ask("[bold white] Nome do livro[/bold white]")
    if not name.strip():
        console.print(Panel("[bold red] O título não pode estar vazio.[/bold red]"))
        return

    author = Prompt.ask("[bold white] Autor[/bold white]")
    if not author.strip():
        console.print(Panel("[bold red] O autor não pode estar vazio.[/bold red]"))
        return

    url = Prompt.ask("[bold white] URL[/bold white]")
    if not url.strip():
        console.print(Panel("[bold red] O URL não pode estar vazio.[/bold red]"))
        return

    tags_input = Prompt.ask("[bold white] Tags (separadas por vírgula)[/bold white]")
    description = Prompt.ask("[bold white] Descrição[/bold white]")

    description = description if description.strip() else None
    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input.strip() else []

    result = database.add_book(name, author, url, tags, description)

    if result["success"]:
        console.print(Panel(f"[green] {result['message']}[/green]"))
    else:
        console.print(Panel(f"[red] {result['message']}[/red]"))

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

@cli.command(name = "delete", help = "Deleta um livro da biblioteca usando seu ID.")
@click.argument("book_id", type = int)
@click.option("--force", "-f", is_flag = True, help = "Deleta sem confirmação")
def delete(book_id: int, force: bool):
    book = database.get_book_details(book_id)
    if not force:
        if click.confirm(f" Tem certeza que deseja deletar '{book['title']}' de {book['author']}?"):
            result = database.delete_book(book_id)
            if result["success"]:
                console.print(Panel(f"[green] {result['message']}[/green]"))
            else:
                console.print(Panel(f"[red] {result['message']}[/red]"))
    else:
        result = database.delete_book(book_id)
        if result["success"]:
            console.print(Panel(f"[green] {result['message']}[/green]"))
        else:
            console.print(Panel(f"[red] {result['message']}[/red]"))

@cli.command(name = "search", help = "Busca livros por um termo no título ou autor(Case Insensitive).",)
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
        console.print(Panel(
                f"[yellow] Nenhum livro encontrado para [bold white]'{term}'[/bold white] em [bold white]{search_label}[/bold white][/yellow]"))
        return

    table_title = f"RESULTADOS DE BUSCA POR {term} - ({len(books)}) em {search_label}"
    table = create_rich_table(books, table_title)

    console.print(table)

@cli.command(help="Atualiza informações de um livro existente.")
@click.argument("book_id", type=int)
@click.option("--title", "-t", help="Novo título")
@click.option("--author", "-a", help="Novo autor")
@click.option("--url", "-u", help="Novo URL")
@click.option("--tags", "-g", help="Substitui tags")
@click.option("--description", "-d", help="Nova descrição")
def edit(book_id, title, author, url, tags, description):
    current = database.get_book_details(book_id)
    if not current:
        console.print(Panel(f"[red]❌ Livro ID {book_id} não encontrado.[/red]")) 
        return
    
    if not any([title, author, url, tags, description]):
        console.print(Panel("[yellow] Forneça pelo menos um campo.[/yellow]\n"))
        return
    
    changes = []
    if title: 
        changes.append(f"Título: '{current['title']}' → '{title}'")
    if author: 
        changes.append(f"Autor: '{current['author']}' → '{author}'")
    if url: 
        changes.append(f"URL: '{current['url']}' → '{url}'")
    if description: 
        changes.append(f"Descrição: '{current['description']}' → '{description}'")
    if tags is not None: 
        changes.append(f"Tags: '{', '.join(current['tags'])}' → '{tags}'")
    
    if changes:
        console.print(Panel("[yellow]Alterações:[/yellow]\n" + "\n".join(changes)))
    
    tags_list = [t.strip() for t in tags.split(",")] if tags and tags.strip() else (None if tags is None else [])
    
    result = database.update_book(book_id, title, author, url, tags_list, description)
    style = "green" if result["success"] else "red"
    console.print(Panel(f"[{style}]{result['message']}[/{style}]"))

@cli.command(help = "Mostra informações detalhadas de um livro.")
@click.argument("book_id", type = int)
def detail(book_id):
    book = database.get_book_details(book_id)

    if not book:
        console.print(Panel(" [bold red]Livro não encontrado[/bold red]"))
        return

    book_id = book["id"]
    title = book["title"]
    author = book["author"]
    url = book["url"]
    tags = ", ".join(book["tags"]) if book.get("tags") else "Sem tags"
    description = book["description"]
    created_at = book["created_at"]

    info_text = f"""[bold cyan]Titulo:[/bold cyan] [bold white]{title}[/bold white]
[bold cyan]Autor:[/bold cyan] [bold white]{author}[/bold white]
[bold cyan]URL:[/bold cyan] [bold white]{url}[/bold white]
[bold cyan]Tags:[/bold cyan] [bold white]{tags}[/bold white]
[bold cyan]Descrição:[/bold cyan] [bold white]{description or "Nenhuma descrição"}[/bold white]
[bold cyan]Adicionado em:[/bold cyan] [bold white]{created_at}[/bold white]"""

    console.print(Panel(info_text, title = f"[bold]ID - {book_id}[/bold]", border_style = "blue", padding = (1, 2)))

def main():
    cli()
    
if __name__ == "__main__":
    main()


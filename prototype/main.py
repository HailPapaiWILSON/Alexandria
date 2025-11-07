import webbrowser
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

import database

console = Console()

@click.group()
def cli():
    database.create_tables()

def create_rich_table(books, table_title):
    table = Table(
        title=table_title,
        show_header=True,
        header_style="bold cyan",
        title_style="bold blue",
        show_lines=True,
        border_style="blue",
        padding=(0, 2),
    )

    table.add_column("ID", style="white", width=4, justify="center")
    table.add_column("Titulo", style="white", width=30, justify="center")
    table.add_column("Autor", style="green", width=17, justify="center")
    table.add_column("Tags", style="yellow", width=17, justify="center")
    table.add_column("Adicionado em", style="cyan", width=12, justify="center")

    for book in books:
        book_id: int = book["id"]
        title: str = book["title"]
        author: str = book["author"]
        url = book["url"]
        tags = book["tags"]
        created_at: str = book["created_at"]

        hyperlink = f"\033]8;;{url}\033\\{title}\033]8;;\033\\"

        title_text = Text.from_ansi(hyperlink)
        title_text.truncate(30, overflow="ellipsis")

        author_text = Text(author)
        author_text.truncate(17, overflow="ellipsis")

        tags_str = ", ".join(tags) if tags else "Sem Tags"
        tags_text = Text(tags_str)
        tags_text.truncate(17, overflow="ellipsis")

        table.add_row(str(book_id), title_text, author_text, tags_text, created_at)
    return table

@cli.command(help="Adiciona um novo livro (título, autor, URL) à biblioteca.")
def add():
    name = Prompt.ask("[bold white] Nome do livro[/bold white]")
    if not name.strip():
        console.print(Panel("[bold red]O título não pode estar vazio.[/bold red]"))
        return

    author = Prompt.ask("[bold white] Autor[/bold white]")
    if not author.strip():
        console.print(Panel("[bold red]O autor não pode estar vazio.[/bold red]"))
        return

    url = Prompt.ask("[bold white] URL[/bold white]")
    if not url.strip():
        console.print(Panel("[bold red]O URL não pode estar vazio.[/bold red]"))
        return

    tags_input = Prompt.ask("[bold white] Tags (separadas por vírgula)[/bold white]")
    description = Prompt.ask("[bold white] Descrição[/bold white]")

    description = description if description.strip() else None
    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input.strip() else []

    result = database.add_book(name, author, url, tags, description)

    if result["success"]:
        console.print(Panel(f"[green]{result['message']}[/green]"))
    else:
        console.print(Panel(f"[red]{result['message']}[/red]"))

@cli.command(name="list", help="Lista todos os livros na biblioteca.")
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

@cli.command(name="delete", help="Deleta um livro da biblioteca usando seu ID.")
@click.argument("book_id", type=int)
@click.option("--force", "-f", is_flag=True, help="Deleta sem confirmação")
def delete(book_id: int, force: bool):
    if not force:
        if click.confirm(f"Tem certeza que deseja deletar livro com ID - {book_id}?"):
            result = database.delete_book(book_id)
            if result["success"]:
                console.print(Panel(f"[green]{result['message']}[/green]"))
            else:
                console.print(Panel(f"[red]{result['message']}[/red]"))
    else:
        result = database.delete_book(book_id)
        if result["success"]:
            console.print(Panel(f"[green]{result['message']}[/green]"))
        else:
            console.print(Panel(f"[red]{result['message']}[/red]"))

@cli.command(name="search", help="Busca livros por um termo no título ou autor(Case Insensitive).",)
@click.argument("term", type=str)
@click.option("--title", "-t", is_flag=True, help="Busca apenas no título")
@click.option("--author", "-a", is_flag=True, help="Busca apenas no autor")
@click.option("--tag", "-g", is_flag=True, help="Busca apenas nas tags")
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
                f"[yellow] Nenhum livro encontrado para [bold white]'{term}'[/bold white][/yellow]"))
        return

    table_title = f"RESULTADOS DE BUSCA POR {term} - ({len(books)})"
    table = create_rich_table(books, table_title)

    console.print(table)

@cli.command(help="Atualiza informaçoes de um livros existente.")
@click.argument("book_id", type=int)
@click.option("--title", "-t", help="Novo Titulo")
@click.option("--author", "-a", help="Novo Autor")
@click.option("--url", "-u", help="Novo URL")
@click.option("--tags", "-g", help="Novas Tags (separadas por vírgula)")
@click.option("--description", "-d", help="Nova Descrição")
def edit(book_id, title, author, url, tags, description):
    if not any([title, author, url, tags, description]):
        console.print(Panel(
                "[bold red] Forneça pelo menos algum campo para atualizar (--title, --author, --url, --tags, --description)[/bold red]"))
        return

    tags_list = None
    if tags is not None:
        tags_list = [tag.strip() for tag in tags.split(",")] if tags.strip() else []

    result = database.update_book(book_id, title, author, url, tags_list, description)
    if result["success"]:
        console.print(Panel(f"[green]{result['message']}[/green]"))
    else:
        console.print(Panel(f"[red]{result['message']}[/red]"))

@cli.command(help="Mostra informações detalhadas de um livro.")
@click.argument("book_id", type=int)
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
[bold cyan]Autor:[/bold cyan]  [bold white]{author}[/bold white]
[bold cyan]URL:[/bold cyan]  [bold white]{url}[/bold white]
[bold cyan]Tags:[/bold cyan]  [bold white]{tags}[/bold white]
[bold cyan]Descrição:[/bold cyan]  [bold white]{description or "Nenhuma descrição"}[/bold white]
[bold cyan]Adicionado em:[/bold cyan]  [bold white]{created_at}[/bold white]"""

    console.print(Panel(
            info_text,
            title=f"[bold]ID - {book_id}[/bold]",
            border_style="blue",
            padding=(1, 2),
        ))

def main():
    cli()
    
if __name__ == "__main__":
    main()


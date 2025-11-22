import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

import utils
import database

console = Console()

@click.group()
def cli() -> None:
    database.create_tables()

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

    result = database.insert_book(name, author, url, tags, description)

    if result["success"]:
        console.print(Panel(f"[green] {result['message']}[/green]"))
    else:
        console.print(Panel(f"[red] {result['message']}[/red]"))

@cli.command(name = "list", help = "Lista todos os livros na biblioteca.")
def list_books():
    total_books = database.count_books()
    if total_books == 0:
        console.print(Panel("[yellow] Sua biblioteca está vazia.[/yellow]"))
        return False

    books = database.fetch_all_books()
    table_title = f"B I B L I O T E C A - {total_books} Livros"
    table = utils.create_rich_table(books, table_title)
    console.print(table)

    return True

@cli.command(name = "delete", help = "Deleta um livro da biblioteca usando seu ID.")
@click.argument("book_id", type = int)
@click.option("--force", "-f", is_flag = True, help = "Deleta sem confirmação")
def delete(book_id: int, force: bool):
    book = database.fetch_book(book_id)
    
    if not force:
        if click.confirm(f" Tem certeza que deseja deletar '{book['title']}' de {book['author']}?"):
            result = database.remove_book(book_id)
            if result["success"]:
                console.print(Panel(f"[green] {result['message']}[/green]"))
            else:
                console.print(Panel(f"[red] {result['message']}[/red]"))
    else:
        result = database.remove_book(book_id)
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
    table = utils.create_rich_table(books, table_title)

    console.print(table)

@cli.command(help="Atualiza informações de um livro existente.")
@click.argument("book_id", type=int)
@click.option("--title", "-t", help="Novo título")
@click.option("--author", "-a", help="Novo autor")
@click.option("--url", "-u", help="Novo URL")
@click.option("--tags", "-g", help="Substitui tags")
@click.option("--description", "-d", help="Nova descrição")
def edit(book_id, title, author, url, tags, description):
    current = database.fetch_book(book_id)
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
        changes.append(f"Descrição: '{current.get('description') or 'Nenhuma'}' → '{description}'")
    if tags is not None: 
        changes.append(f"Tags: '{', '.join(current.get('tags', [])) or 'Sem tags'}' → '{tags}'")
    
    if changes:
        console.print(Panel("[yellow]Alterações:[/yellow]\n" + "\n".join(changes)))
    
    tags_list = [t.strip() for t in tags.split(",")] if tags and tags.strip() else (None if tags is None else [])
    
    result = database.modify_book(book_id, title, author, url, tags_list, description)
    style = "green" if result["success"] else "red"
    console.print(Panel(f"[{style}]{result['message']}[/{style}]"))

@cli.command(help = "Mostra informações detalhadas de um livro.")
@click.argument("book_id", type = int)
def detail(book_id):
    book = database.fetch_book(book_id)

    if not book:
        console.print(Panel(" [bold red]Livro não encontrado[/bold red]"))
        return

    book_id = book["id"]
    title = book["title"]
    author = book["author"]
    url = book["url"]
    tags = ", ".join(book["tags"]) if book.get("tags", []) else "Sem tags"
    description = book.get("description")
    created_at = utils.convert_date_format(book["created_at"])

    progress = database.get_reading_progress(book_id)
    progress_txt = f"Capitulo {progress["chapter"] or "N/A"}, Pagina {progress["page"] or "N/A"}" if progress else "Nenhum progresso registrado"

    info_text = f"""[bold cyan]Titulo:[/bold cyan] [bold white]{title}[/bold white]
[bold cyan]Autor:[/bold cyan] [bold white]{author}[/bold white]
[bold cyan]URL:[/bold cyan] [bold white]{url}[/bold white]
[bold cyan]Tags:[/bold cyan] [bold white]{tags}[/bold white]
[bold cyan]Descrição:[/bold cyan] [bold white]{description or "Nenhuma descrição"}[/bold white]
[bold cyan]Adicionado em:[/bold cyan] [bold white]{created_at}[/bold white]
[bold cyan]Progresso:[/bold cyan] [bold white]{progress_txt}[/bold white]"""

    console.print(Panel(info_text, title = f"[bold]ID - {book_id}[/bold]", border_style = "blue", padding = (1, 2)))

@cli.command(help = "Registra ou atualiza o progresso de leitura (capítulo e página).")
@click.argument("book_id", type = int)
@click.option("--chapter", "-c", type = int, help = "Capitulo atual")
@click.option("--page", "-p", type = int, help = "Pagina atual")
def progress(book_id, chapter, page):
    book = database.fetch_book(book_id)
    if not book:
        console.print(Panel(f"[red]Livro '{book["title"]}' de {book["author"]} nao encontrado[/red]"))
        return
    result = database.update_reading_progress(book_id, chapter, page)
    style = "green" if result["success"] else "red"
    console.print(Panel(f"[{style}]{result['message']}[/{style}]"))


def main():
    cli()
    
if __name__ == "__main__":
    main()


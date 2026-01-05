import click
import subprocess
import utils
import database

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

@click.group()
def cli() -> None:
    database.create_tables()

@cli.command(help="Adiciona um novo livro (título, autor, URL) à biblioteca.")
def add():
    title = Prompt.ask("[bold white] Titulo[/bold white]")
    if not title.strip():
        console.print(Panel.fit("[bold red]O título não pode estar vazio.[/bold red]"))
        return

    author = Prompt.ask("[bold white] Autor[/bold white]")
    if not author.strip():
        console.print(Panel.fit("[bold red]O autor não pode estar vazio.[/bold red]"))
        return

    url = Prompt.ask("[bold white] URL[/bold white]")
    if not url.strip():
        console.print(Panel.fit("[bold red]O URL não pode estar vazio.[/bold red]"))
        return

    tags_input = Prompt.ask("[bold white] Tags (separadas por vírgula)[/bold white]")
    description = Prompt.ask("[bold white] Descrição[/bold white]")

    description = description.strip() or None
    tags = utils.parse_tags(tags_input)

    result = database.insert_book(title, author, url, tags, description)

    utils.print_result(result, console)

@cli.command(help= "Deleta um livro da biblioteca usando seu ID.")
@click.option("--force", "-f", is_flag=True, help="Deleta sem confirmação")
def delete(force: bool):
    book_id = select_book(prompt="Deletar > ")
    if not book_id:
        return

    book = database.fetch_book(book_id)
    
    if not force:
        if click.confirm(f"Tem certeza que deseja deletar '{book['title']}' de {book['author']}?"):
            result = database.remove_book(book_id)
            utils.print_result(result, console)
    else:
        result = database.remove_book(book_id)
        utils.print_result(result, console)

@cli.command(help="Atualiza informações de um livro existente.")
def edit():
    book_id = select_book(prompt="Editar > ")
    if not book_id:
        return

    current = database.fetch_book(book_id)
    console.print(Panel.fit(f"[cyan]Editando: {current['title']} - {current['author']}[/cyan]"))
    console.print("[dim]Edite o texto ou pressione Enter para manter[/dim]\n")

    new_title = utils.prefill_prompt("Titulo", current['title'])
    new_author = utils.prefill_prompt("Autor", current['author'])
    new_url = utils.prefill_prompt("URL", current['url'])
    
    current_tags = utils.format_tags(current.get('tags', []))
    tags_input = utils.prefill_prompt("Tags", current_tags)

    current_description = current.get('description', '')
    new_description = utils.prefill_prompt("Descriçao", current_description)
    
    changes = []
    if new_title != current['title']: 
        changes.append(f"Título: '{current['title']}' → '{new_title}'")
    if new_author != current['author']: 
        changes.append(f"Autor: '{current['author']}' → '{new_author}'")
    if new_url != current['url']: 
        changes.append(f"URL: '{current['url']}' → '{new_url}'")
    if new_description != current['description']:
        changes.append(f"Descrição: '{current.get('description') or 'Nenhuma'}' → '{new_description}'")

    new_tags_list = utils.parse_tags(tags_input)

    if new_tags_list != current['tags']: 
        changes.append(f"Tags: '{utils.format_tags(current.get('tags', []))}' → '{utils.format_tags(new_tags_list)}'")
    
    if changes:
        console.print(Panel.fit("[yellow]Alterações:[/yellow]\n" + "\n".join(changes)))
    else:
        console.print(Panel.fit("[dim]Nenhuma alteraçao realizada[/]"))
        return

    update_result = database.modify_book(book_id, new_title, new_author, new_url, new_tags_list, new_description)

    utils.print_result(update_result, console)

@cli.command(help="Mostra informações detalhadas de um livro")
def find():
    book_id = select_book(prompt="Livro > ")

    if not book_id:
        return

    book = database.fetch_book(book_id)

    if not book:
        console.print(Panel.fit("[bold red]Livro não encontrado[/bold red]"))
        return

    book_id = book["id"]
    title = book["title"]
    author = book["author"]
    url = book["url"]
    tags = utils.format_tags(book['tags'])
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

    console.print(Panel.fit(info_text, title = f"[bold]ID - {book_id}[/bold]", border_style = "blue", padding = (1, 2)))

@cli.command(help="Registra ou atualiza o progresso de leitura (capítulo e página).")
def progress():
    book_id = select_book(prompt="Progresso > ")
    if not book_id:
        return
    
    book = database.fetch_book(book_id)
    
    console.print(Panel.fit(f"[cyan]Atualizando progresso: {book['title']} - {book['author']}[/]"))
    console.print('[dim]Edite ou pressione Enter para manter[/]')

    current_progress = database.get_reading_progress(book_id)
    current_chap = str(current_progress['chapter']) if current_progress and current_progress['chapter'] else ""
    current_page = str(current_progress['page']) if current_progress and current_progress['page'] else ""
    
    new_chapter = utils.prefill_prompt("Capitulo", current_chap)
    new_page = utils.prefill_prompt("Pagina", current_page)

    chapter = int(new_chapter) if new_chapter.strip() else None
    page = int(new_page) if new_page.strip() else None

    result = database.update_reading_progress(book_id, chapter, page)
    utils.print_result(result, console)

def select_book(prompt):
    books = database.fetch_all_books()

    if not books:
        console.print(Panel.fit("[yellow] Sua biblioteca está vazia.[/]"))
        return

    lines = []
    book_map = {}

    for book in books:
        tags_str = utils.format_tags(book['tags'])
        line = f"{book['title']} | {book['author']}"
        book_map[line] = book['id']

        lines.append(line)
    
    fzf_input = "\n".join(lines)
    
    fzf_output = subprocess.run(
        ['fzf', f'--prompt={prompt}', '--height=40%', '--layout=reverse', '--border'],
        input = fzf_input,
        text=True,
        capture_output=True
    )

    if fzf_output.returncode == 0:
        selected = fzf_output.stdout.strip()
        return book_map[selected]
    return None

def main():
    cli()
    
if __name__ == "__main__":
    main()


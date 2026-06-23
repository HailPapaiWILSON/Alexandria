import click
import subprocess
import utils
import database


from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.columns import Columns
from rich import box


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

    tags = Prompt.ask("[bold white] Tags (separadas por vírgula)[/bold white]")

    description = Prompt.ask("[bold white] Descrição[/bold white]")

    result = database.insert_book(title, author, url, tags.strip() or None, description.strip() or None)

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
    new_tags = utils.prefill_prompt("Tags", current.get('tags') or '')
    new_description = utils.prefill_prompt("Descriçao", current.get('description') or '')
    
    changes = []

    if new_title != current['title']: 
        changes.append(f"Título: '{current['title']}' → '{new_title}'")
    if new_author != current['author']: 
        changes.append(f"Autor: '{current['author']}' → '{new_author}'")
    if new_url != current['url']: 
        changes.append(f"URL: '{current['url']}' → '{new_url}'")
    if new_tags != (current.get('tags') or ''):
        changes.append(f"Tags: '{current.get('tags') or ''}' → '{new_tags}'")
    if new_description != (current.get('description') or ''):
        changes.append(f"Descrição: '{current.get('description') or ''}' → '{new_description}'")

    if changes:
        console.print(Panel.fit("[yellow]Alterações:[/yellow]\n" + "\n".join(changes)))
    else:
        console.print(Panel.fit("[dim]Nenhuma alteraçao realizada[/]"))
        return

    update_result = database.modify_book(
            book_id, new_title, new_author, new_url,
            new_tags.strip(), new_description.strip()
    )

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

    progress = database.get_reading_progress(book['id'])

    table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(style="white")

    table.add_row("Título",     f"[link={book['url']}]{book['title']}[/link]")
    table.add_row("Autor",      book['author'])
    table.add_row("URL",        f"[link={book['url']}]{book['url'][:20]}...[/link]")
    table.add_row("Tags",       book.get('tags') or "[dim]Nenhuma[/dim]")
    table.add_row("Descrição",  book.get('description') or "[dim]Nenhuma[/dim]")
    table.add_row("Adicionado", utils.convert_date_format(book['created_at']))

    progress_table = Table(show_header=True, box=box.ROUNDED, padding=(0, 2))
    progress_table.add_column("Capítulo", style="bold cyan", justify="center")
    progress_table.add_column("Página",   style="bold cyan", justify="center")

    if progress:
        progress_table.add_row(
            str(progress['chapter']) if progress['chapter'] else "[dim]—[/dim]",
            str(progress['page'])    if progress['page']    else "[dim]—[/dim]",
        )
    else:
        progress_table.add_row("[dim]—[/dim]", "[dim]—[/dim]")

    console.print(Panel(
        Columns([table, progress_table], equal=False, expand=False),
        border_style="blue",
        padding=(1, 2),
        expand=False
    ))


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


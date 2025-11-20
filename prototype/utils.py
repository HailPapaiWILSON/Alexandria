from datetime import datetime
from rich.table import Table
from rich.text import Text
import rich.box
import database

def convert_date_format(date_str):
    formated: str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    return formated

def create_rich_table(books, table_title):
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
    table.add_column("Progresso", style="magenta", justify="center", no_wrap=True)

    for book in books:
        book_id: int = book["id"]
        title: str = book["title"]
        author: str = book["author"]
        url: str = book["url"]
        tags: list[str] = book["tags"]
        created_at: str = convert_date_format(book["created_at"])
        progress: str = database.get_reading_progress(book["id"])

        if progress and (progress["page"] or progress["chapter"]):
            part = []
            if progress["chapter"]:
                part.append(f"Cap {progress['chapter']}")
            if progress["page"]:
                part.append(f"Pag {progress['page']}")
            progress_txt = ", ".join(part) if part else "-"
        else:
            progress_txt = "-"


        hyperlink: str = f"\033]8;;{url}\033\\{title}\033]8;;\033\\"

        title_text = Text.from_ansi(hyperlink)

        tags_str: str = ", ".join(tags) if tags else "Sem Tags"
        tags_text: Text = Text(tags_str)

        table.add_row(
            str(book_id), 
            title_text, 
            author, 
            tags_text, 
            created_at,
            progress_txt
        )
    return table
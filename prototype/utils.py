from datetime import datetime
import readline
from rich.panel import Panel



def convert_date_format(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")


def prefill_prompt(label, prefilled_text):
    readline.set_startup_hook(lambda: readline.insert_text(prefilled_text))
    try:
        return input(f"\033[1m {label}: \033[0m")
    finally:
        readline.set_startup_hook()


def print_result(result, console):
    if result['success']:
        console.print(Panel.fit(f"[green]{result['message']}[/]"))
    else:
        console.print(Panel.fit(f"[red]{result['message']}[/]"))

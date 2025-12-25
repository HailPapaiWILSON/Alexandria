from datetime import datetime
from rich.prompt import Prompt
import readline


def convert_date_format(date_str):
    formated: str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    return formated

def parse_tags(input_tags):
    if not input_tags:
        return []

    stripped_tags = input_tags.strip()

    if not stripped_tags:
        return []
    
    split_tags = stripped_tags.split(',')

    result_tags = []

    for tag in split_tags:
        clean_tags = tag.strip()

        if clean_tags:
            result_tags.append(clean_tags)

    return result_tags

def format_tags(tags_list):
    if tags_list:
        return ', '.join(tags_list)
    return "Sem tags"

def prefill_prompt(label, prefilled_text):
    readline.set_startup_hook(lambda: readline.insert_text(prefilled_text))
    try:
        return Prompt.ask(f"[bold white] {label}[/]", show_default=False)
    finally:
        readline.set_startup_hook()


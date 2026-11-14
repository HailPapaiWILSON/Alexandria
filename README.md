# Alexandria

A command-line application for managing your personal book library. Track books, organize them with tags, and monitor your reading progress, all from the terminal.

## Features

- Add books with title, author, URL, tags, and description
- Edit existing book entries
- Delete books from your library
- Search and select books with fuzzy finding (fzf)
- Track reading progress by chapter and page
- Duplicate detection when adding books
- SQLite database stored in your home directory

## Requirements

- Python 3.14 or higher
- [fzf](https://github.com/junegunn/fzf)
- [uv](https://docs.astral.sh/uv/)

## Installation

### Install Alexandria

Clone the repository and install it using uv:

```bash
git clone https://github.com/HailPapaiWILSON/Alexandria
cd alexandria
uv sync
```

To install the application globally as a tool:

```bash
uv tool install .
```

This makes the `alex` command available system-wide.

Alternatively, run commands directly through uv without global installation:

```bash
uv run alex add
```

## Commands

The application is invoked through the `alex` command. If you installed it with `uv tool install`, use `alex` directly. Otherwise, prefix commands with `uv run`.

| Command | Description |
| --- | --- |
| `alex add` | Add a new book. Prompts for title, author, URL, tags (comma-separated), and description. Title, author, and URL are required. Duplicate titles by the same author are rejected. |
| `alex find` | Select a book via fzf and display a panel with its title, author, URL, tags, description, date added, and current reading progress. |
| `alex edit` | Select a book via fzf and edit its fields. Each field is pre-filled with the current value; press Enter to keep it. A summary of changes is shown before saving. |
| `alex progress` | Select a book via fzf and update its reading progress by chapter and page. Leave a field empty to keep the existing value. |
| `alex delete` | Select a book via fzf and confirm deletion. Use `--force` or `-f` to skip confirmation. |

### Delete options

| Option | Description |
| --- | --- |
| `--force`, `-f` | Delete the selected book without asking for confirmation. |

Example:

```bash
alex delete --force
```

## Database

Alexandria stores its data in a SQLite database located at:

- Linux/macOS: `~/.local/alexandria/alexandria.db`
- Windows: `%USERPROFILE%\AppData\alexandria\alexandria.db`

The database schema is created automatically on first run. Two tables are used:

- `books`: stores book metadata (title, author, URL, tags, description, creation date)
- `reading_progress`: stores chapter and page per book, linked by foreign key with cascade delete

## Project Structure

```
src/alexandria/
    main.py       CLI commands and user interaction
    database.py   Database connection and CRUD operations
    utils.py      Prompt helpers and formatting utilities
```

import webbrowser
import database
import os

def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def prompt_add() -> None:
    name: str = input("Nome do livro: ")
    author: str = input("Autor: ")
    url: str = input("URL: ")
    if not name or not author or not url:
        print("❌ Por favor, insira um nome, autor e URL válidos.")
        return
    database.add_book(name, author, url)

def prompt_list() -> bool:
    total_books: int = database.book_count()
    if total_books == 0:
        print("\n📚 Sua biblioteca está vazia.")
        return False
    
    print("\n------ B I B L I O T E C A ------\n")
    print(f"📖 Total de Livros: {total_books}\n")

    books: list[tuple] = database.list_books()

    for book in books:
        book_id: int = book[0]
        title: str = book[1]
        author: str = book[2]
        created_at: str = book[4]

        print(f"[{book_id}] {title}")
        print(f"     👤 por {author}")
        print(f"     🗓️ Adicionado: {created_at}")
        print("--------------------------------------------------")
    return True

def prompt_open() -> None:
    try:
        book_id: int = int(input("\nDigite o ID do livro para abrir: "))
        url: str | None = database.open_book(book_id)
        if url:
            webbrowser.open(url)
        else:
            print("Livro não encontrado.")
    except ValueError:
        print("❌ Por favor, insira um ID válido.")

def prompt_delete() -> None:
    try:
        book_id: int = int(input("\nDigite o ID do livro para deletar: "))
        database.delete_book(book_id)
    except ValueError:
        print("❌ Por favor, insira um ID válido.")

def prompt_search() -> None:
    clear()
    print("\n------ B U S C A R ------\n")
    
    try: 
        term: str = input("🔍 Digite o termo de busca: ")
    except ValueError:
        print("❌ Por favor, insira um termo válido.")
        return
    books: list[tuple] = database.search_books(term)

    if not books:
        print("❌ Termo não encontrado.")
        return
    
    print(f"------- RESULTADOS DE BUSCA POR {term} - ({len(books)}) -------")
    print(f"📖 Total de Livros: {len(books)}\n")

    for book in books:
        book_id: int = book[0]
        title: str = book[1]
        author: str = book[2]
        created_at: str = book[4]

        print(f"[{book_id}] {title}")
        print(f"     👤 por {author}")
        print(f"     🗓️ Adicionado: {created_at}")
        print("--------------------------------------------------")

def main() -> None:
    database.create_tables()
    while True:
        clear()
        print("\n------ A L E X A N D R I A ------\n")
        print("1. 🌟 Adicionar um livro")
        print("2. 📚 Listar sua biblioteca")
        print("3. 🌐 Abrir um livro")
        print("4. 🗑️ Deletar um livro")
        print("5. 🔍 Buscar um livro")
        print("6. 🚪 Sair")
        print("---------------------------------------\n")
        choice: str = input("\n👉 Escolha uma opção: ")

        if choice == "1":
            prompt_add()
        elif choice == "2":
            prompt_list()
        elif choice == "3":
            prompt_list()
            prompt_open()
        elif choice == "4":
            prompt_list()
            prompt_delete()
        elif choice == "5":
            prompt_search()
        elif choice == "6":
            break
        else:
            print("❌ Opção inválida. Tente novamente.")
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
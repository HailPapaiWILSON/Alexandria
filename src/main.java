import java.util.Scanner;
import java.sql.SQLException;

public class Main
{
    public static void Prompt_Add()
    {
        Scanner scan = new Scanner(System.in);

        System.out.println("Nome do Livro: ");
        String title = scan.nextLine();
        System.out.println("Autor do Livro: ");
        String author = scan.nextLine();
        System.out.println("url do livro: ");
        String url = scan.nextLine();

        try
        {
            database.Add_Book(title, author, url);
        }
        catch(SQLException e)
        {
            System.out.println("Erro ao adicionar o livro: " + e.getMessage());
        }
    }

    public static void main(String[] args)
    {
        try
        {
            database.Create_Tables();
        }
        catch(SQLException e)
        {
            System.out.println("Erro ao gerar tabela: " + e.getMessage());
        }

        Scanner scan = new Scanner(System.in);

        while(true)
        {
            System.out.println("----BEM VINDO A ALEXANDRIA----");
            System.out.println("1. 🌟 Adicionar um livro");
            System.out.println("2. 🚪 Sair");
            
            int choice = scan.nextInt();
            scan.nextLine();

            if(choice == 1)
            {
                Prompt_Add();
            }
            else if(choice == 2)
            {
                System.out.println("Saindo...");
                break;
            }
        }
    }
}


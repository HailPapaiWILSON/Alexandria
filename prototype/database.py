import java.sql.*;

public class database
{
    static Connection Connect_Database() throws SQLException
    {
        String url = "jdbc:mysql://localhost:3306/MYSQL";
        String user = "root";
        String pass = "batata";

        try {
            Connection conn = DriverManager.getConnection(url, user, pass);
            conn.close();
        } catch (SQLException e) {
            System.out.println("❌ Erro ao conectar:");
            e.printStackTrace();
        }
        return(
            DriverManager.getConnection(url, user, pass)
        );
    }

    public static void Create_Tables() throws SQLException
    {
        Connection conn = Connect_Database();
        Statement stmt = conn.createStatement();

    stmt.executeUpdate(
            """
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,                   
            author VARCHAR(255) NOT NULL,                  
            url VARCHAR(255) NOT NULL,                    
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        );

        stmt.close();
        conn.close();
    }

    public static void Add_Book(String title, String author, String url ) throws SQLException
    {
        Connection conn = Connect_Database();
        PreparedStatement ps = conn.prepareStatement(
                """
                INSERT INTO books (title, author, url)
                VALUES (?, ?, ?);
                """);
        ps.setString(1, title);
        ps.setString(2, author);
        ps.setString(3, url);
        ps.executeUpdate(); 
        System.out.println("Adicionado " + title + " por " + author + " a sua biblioteca");
        
        ps.close();
        conn.close();
    }

    public static void Delete_Books(int id) throws SQLException
    {
        Connection conn = Connect_Database();
        PreparedStatement ps = conn.prepereStatement("DELETE FROM books WHERE id = ?;");

        ps.setString(1, id);
        ps.executeUpdate();
        System.out.println("livro de id: " + id + " deletado com sucesso");

        ps.close();
        conn.close();
    }

    public static int Book_Count() throws SQLException
    {
        Connection conn = Connect_Database();
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM books;");
        int count = 0;
        if(rs.next())
        {
            count = rs.getInt(1);
        }

        conn.close();
        rs.close();
        stmt.close();
        return count;
    }

    public static void List_Books() throws SQLException
    {
        Connection conn = Connect_Database();
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM books ORDER BY created_at DESC"); 

        while(rs.next())
        {
            int id = rs.getInt("id");
            String title = rs.getString("title");
            String author = rs.getString("author");
            String created_at = rs.getString("created_at");

            System.out.println("[" + id + "]" + title);
            System.out.println("     por " + author);
            System.out.println("     Adicionado:" + created_at);
            System.out.println("--------------------------------------------------");
        }
        conn.close();
        rs.close();
    }
}

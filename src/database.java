import java.sql.*;

public class database
{
    static Connection Connect_Database() throws SQLException{
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

    public static void Create_Tables() throws SQLException{
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

    public static void Add_Book(String title, String author, String url ) throws SQLException{
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

    public static int Book_Count() throws SQLException{
        Connection conn = Connect_Database();
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM books;");
        int count = rs.getInt(0);

        conn.close();
        return count;
    }

    // static void List_Books() throws SQLException()
    // {

    // }
}


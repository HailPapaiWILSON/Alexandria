import java.sql.*;

public class database
{
    String DB_NAME = "alexandria.sql";

    static Connection conect_database() throws SQLExeption()
    {
        return DriverManager.getConnection(
            "jdbc:mysql://localhost:3306/alexandria.sql"
        )
    }

    static void create_tables() throws SQLExeption()
    {
        Connection conn = conect_database();
        Statement stmt = conn.createStatement();

    stmt.executeUpdate(
            """
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT,
            title VARCHAR(255) NOT NULL,                   
            author VARCHAR(255) NOT NULL,                  
            url VARCHAR(255) NOT NULL,
            description VARCHAR(255)                    
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        );

        stmt.close();
        conn.close();
    }

    static void Add_Book() throws SQLExeption()
    {
        Connection conn = conect_database();
        PreparedStatement ps = conn.createStatement(
                """
                INSERT INTO books (title, author, url)
                VALUES (?, ?, ?);
                """);

        while(rs.next())
        {
            int id = rs.getInt("id");
            String title = rs.getString("title");
            String author = rs.getString("author");
            String url = rs.getString("url");
        }
        System.ou.println("Adicionado" + title + "por" + author + "a sua biblioteca");

        ps.close();
        conn.close();
    }
}
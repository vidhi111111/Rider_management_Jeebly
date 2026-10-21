
import getpass
import psycopg2


def check_database():
    password = getpass.getpass("PostgreSQL password: ")
    connection = None

    try:
        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="postgres",
            user="postgres",
            password=password,
            connect_timeout=5
        )

        cursor = connection.cursor()

        # Check connection details
        cursor.execute("""
            SELECT
                current_database(),
                current_user,
                current_schema(),
                version()
        """)

        print("\n========== CONNECTION DETAILS ==========")
        print("Database, User, Schema, Version:")
        print(cursor.fetchone())

        # List all local databases
        cursor.execute("""
            SELECT datname
            FROM pg_database
            WHERE datistemplate = false
            ORDER BY datname
        """)

        print("\n========== LOCAL DATABASES ==========")
        databases = cursor.fetchall()

        for database in databases:
            print("-", database[0])

        # List tables in the current database's public schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        print("\n========== TABLES IN POSTGRES DATABASE ==========")
        tables = cursor.fetchall()

        if tables:
            for table in tables:
                print("-", table[0])
        else:
            print("No tables found in the public schema.")

        cursor.close()

        print("\nDatabase verification completed successfully.")

    except psycopg2.Error as error:
        print("\nDatabase check failed:")
        print(error)

    finally:
        if connection is not None:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    check_database()

import psycopg2
import os


class Database:

    def __init__(self, host: str, user: str, password: str, db_name: str, port) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.port = port

        # Set Connection to None
        self.connection = None

    @classmethod
    def initialize_from_env(cls) -> None:
        # Extract Secrets
        host = "34.135.163.144"
        user = "postgres"
        password = "mgispostgres"
        db_name = "lab3"
        port = "5432"

        # Return Instance
        return cls(host, user, password, db_name, port)

    def connect(self) -> None:
        self.connection = psycopg2.connect(
            host=self.host,
            database=self.db_name,
            user=self.user,
            password=self.password,
            port=self.port,
        )

    def query(self, query: str) -> str:
        # Open Cursor
        with self.connection.cursor() as c:
            # Try to Execute
            try:
                # Execute Query
                c.execute(query)

                # Commit to DB
                self.connection.commit()

                # Return Output
                return c.fetchall()

            except Exception as e:
                # Roll Back Transaction if Invalid Query
                self.connection.rollback()

                # Display Error
                return "Error: " + e

    def close(self):
        # Close Connection
        self.connection.close()

        # Set Connection to None
        self.connection = None
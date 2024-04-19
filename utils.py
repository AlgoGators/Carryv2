import pandas as pd
import psycopg2
import toml
from typing import Dict, Any
from psycopg2.extensions import connection as PGConnection


config_data: Dict[str, Any] = toml.load(r'config.toml')

# Setup PostgreSQL database parameters from the configuration data for later connection.
DB_PARAMS: Dict[str, Any] = {
    'dbname': config_data['database']['db_carry'],
    'user': config_data['database']['user'],
    'password': config_data['database']['password'],
    'host': config_data['server']['ip'],
    'port': config_data['database']['port']
}


def get_connection() -> PGConnection:
    """
    Establishes a connection to the PostgreSQL database.

    :return: A connection object to the PostgreSQL database.
    """
    # Establish and return a connection object to the PostgreSQL database using psycopg2.
    conn: PGConnection = psycopg2.connect(**DB_PARAMS)

    return conn


def get_data_from_db(symbol: str) -> pd.DataFrame:
    """
    Retrieves historical price data for the contract from the PostgreSQL database.

    :param symbol: The symbol of the contract.
    :return: A pandas DataFrame containing the price data.
    """

    # Get a database connection.
    conn: PGConnection = get_connection()

    # Open a new database cursor for executing SQL commands.
    with conn.cursor() as cur:
        create_table_query: str = f"""
        SELECT * FROM "{symbol}_Data_Carry";
        """
        # Execute the SQL query to create a new table for the symbol.
        cur.execute(create_table_query)
        # Fetch all the rows from the result of the executed query.
        rows = cur.fetchall()
        # Convert the rows into a pandas DataFrame.
        df = pd.DataFrame(rows)

        # Add column names to the DataFrame.
        df.columns = ['symbol', 'date', 'front_price', 'front_expiration', 'further_price', 'further_expiration']

        # Close the cursor.
        cur.close()
        # Close the connection.
        conn.close()

    return df

import psycopg2


def db_connection():
    """ function to open connection """
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='flask',
        user='postgres',
        password='admin'
    )
    return conn

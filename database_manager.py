import psycopg2


class Database:
    conn = None
    cursor = None

    def __init__(self, user, password, server, port):
        print(user)
        conn = psycopg2.connect(host=server, port=port, user=user, password=password, database="CCHS Database")
        cursor = conn.cursor()
        print("connected")

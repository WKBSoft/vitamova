import psycopg2

class spanish:
    def __init__(self, conn):
        self.conn = conn

    def test(self):
        return "test"
import psycopg2

class Spanish:
    def __init__(self, conn):
        self.conn = conn

    def test(self):
        return "test"
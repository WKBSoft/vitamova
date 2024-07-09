import psycopg2
import os

# Create environment variables
def source_profile(file_path):
    with open(file_path) as f:
        for line in f:
            if line.startswith('export '):
                # Strip out 'export ' and split by '=' to get the key and value
                key, value = line[len('export '):].strip().split('=', 1)
                # Remove surrounding quotes from value if they exist
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                os.environ[key] = value

# Use the function to source the profile
source_profile(os.path.expanduser("~/.profile"))

# Database connection
def connect():
    return psycopg2.connect(
        dbname="vitamova",
        user="vitamova",
        password=os.environ.get('db_password'),
        host="db.evenstarsec.local",
        port="5432"
    )

class spanish:
    def __init__(self, conn):      
        self.conn = connect()

    def add(self, word, definition, example):
        with self.conn.cursor() as cur:
            #Check if the word is already in the database
            cur.execute("SELECT * FROM dictionary_es WHERE word=%s",(word,))
            #If the word is not in the database, will add it
            #First we need to create a new id for the word based on the number of rows in the database
            if cur.fetchone() != None:
                #return the id
                return cur.fetchone()[0]
            else:
                cur.execute("SELECT COUNT(*) FROM dictionary_es")
                id = cur.fetchone()[0]
                cur.execute("INSERT INTO dictionary_es VALUES (%s,%s,%s,%s)",(id,word,definition,example))
                self.conn.commit()
                return id

    
class vocabulary:
    def __init__(self, conn):
        self.conn = connect()

    def add(self, username, word_id, language):
        pass

class user_info:
    def __init__(self, conn):
        self.conn = connect()

    class get(self, username):
        def __init__(self, parent, username):
            self.parent = parent
            self.username = username
        def language(self):
            with self.conn.cursor() as cur:
                cur.execute("SELECT language FROM user_info WHERE username=%s",(self.username,))
                return cur.fetchone()[0]
        def last_article_read(self):
            with self.conn.cursor() as cur:
                cur.execute("SELECT last_article_read FROM user_info WHERE username=%s",(self.username,))
                return cur.fetchone()[0]
        def points(self):
            with self.conn.cursor() as cur:
                cur.execute("SELECT points FROM user_info WHERE username=%s",(self.username,))
                return cur.fetchone()[0]
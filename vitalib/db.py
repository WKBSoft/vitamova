import psycopg2
import os
import datetime

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
class connection:
    @staticmethod
    def open():
        conn = psycopg2.connect(
            dbname="vitamova",
            user="vitamova",
            password=os.environ.get('db_password'),
            host="db.evenstarsec.local",
            port="5432"
        )
        return conn
    @staticmethod
    def close(conn):
        conn.close()

#Retrieve user information
class user_info:
    class get:
        def __init__(self, conn, username):
            self.username = username
            self.conn = conn

        def language(self):
            with self.conn.cursor() as cur:
                cur.execute("SELECT language FROM user_info WHERE username=%s", (self.username,))
                return cur.fetchone()[0]

        def last_article_read(self):
            with self.conn.cursor() as cur:
                cur.execute("SELECT last_article_read FROM user_info WHERE username=%s", (self.username,))
                return cur.fetchone()[0]

        def points(self):
            with self.conn.cursor() as cur:
                cur.execute("SELECT points FROM user_info WHERE username=%s", (self.username,))
                return cur.fetchone()[0]

class vocabulary:
    @staticmethod
    def add(conn, username, word, definition, example):
        #Get language from username using user_info class
        language = user_info.get(conn,username).language()
        vocab_table = "vocabulary_"+language
        dict_table = "dictionary_"+language
        #if the word is not in the dictionary, add it with the definition and example
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM "+dict_table+" WHERE word=%s", (word,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO "+dict_table+" (word, definition, example) VALUES (%s, %s, %s)", (word, definition, example))
        #Get the id of the word from the dictionary
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM "+dict_table+" WHERE word=%s", (word,))
            word_id = cur.fetchone()[0]
        #Now insert the word_id, username, a level of 0, and next_review as tomorrow
        tomorrow = str((datetime.datetime.now() + datetime.timedelta(days=1)).date())
        with conn.cursor() as cur:
            cur.execute("INSERT INTO "+vocab_table+" (word_id, username, level, next_review) VALUES (%s, %s, 0, %s)", (word_id, username, tomorrow))

    class level:
        def __init__(self, conn, username):
            self.conn = conn
            self.username = username
            #Get the language from the username using user_info class
            self.language = user_info.get(self.conn, self.username).language()
        def increase(self, username, word_id):
            #We will use the ebbinghaus forgetting curve to determine the next review date
            #If the current level is 0, increase to 1 and the next review is 3 days from now
            #If the current level is 1, increase to 2 and the next review is 7 days from now
            #If the current level is 2, increase to 3 and the next review is 14 days from now
            #If the current level is 3, increase to 4 and the next review is 30 days from now
            #If the current level is 4, increase to 5 and the next review is 60 days from now
            #If the current level is 5, increase to 6 and the next review is in year 3000
            #6 is the highest level
            with self.conn.cursor() as cur:
                cur.execute("SELECT level FROM vocabulary_"+self.language+" WHERE username=%s AND word_id=%s", (username, word_id))
                level = cur.fetchone()[0]
            if level == 0:
                next_review = str((datetime.datetime.now() + datetime.timedelta(days=3)).date())
                level = 1
            elif level == 1:
                next_review = str((datetime.datetime.now() + datetime.timedelta(days=7)).date())
                level = 2
            elif level == 2:
                next_review = str((datetime.datetime.now() + datetime.timedelta(days=14)).date())
                level = 3
            elif level == 3:
                next_review = str((datetime.datetime.now() + datetime.timedelta(days=30)).date())
                level = 4
            elif level == 4:
                next_review = str((datetime.datetime.now() + datetime.timedelta(days=60)).date())
                level = 5
            elif level == 5:
                next_review = "3000-01-01"
                level = 6
            with self.conn.cursor() as cur:
                cur.execute("UPDATE vocabulary_"+self.language+" SET level=%s, next_review=%s WHERE username=%s AND word_id=%s", (level, next_review, username, word_id))

        def reset(self):
            #Reset all levels to 0 and next review to tomorrow
            tomorrow = str((datetime.datetime.now() + datetime.timedelta(days=1)).date())
            with self.conn.cursor() as cur:
                #remember the language is in self.language
                cur.execute("UPDATE vocabulary_"+self.language+" SET level=0, next_review=%s", (tomorrow,))
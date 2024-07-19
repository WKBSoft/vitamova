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
        #Commit changes and close the connection
        conn.commit()
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
    class update:
        def __init__(self, conn, username):
            self.username = username
            self.conn = conn
        
        def points(self, add_points):
            #Add add_points to the current points
            with self.conn.cursor() as cur:
                cur.execute("SELECT points FROM user_info WHERE username=%s", (self.username,))
                points = cur.fetchone()[0]
            points += add_points
            with self.conn.cursor() as cur:
                cur.execute("UPDATE user_info SET points=%s WHERE username=%s", (points, self.username))
            #return the new points
            return points
        def language(self, language):
            with self.conn.cursor() as cur:
                cur.execute("UPDATE user_info SET language=%s WHERE username=%s", (language, self.username))

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
                print("Word", word, "is not in the dictionary, adding it now")
                cur.execute("INSERT INTO "+dict_table+" (word, definition, example) VALUES (%s, %s, %s)", (word, definition, example))
        #Get the id of the word from the dictionary
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM "+dict_table+" WHERE word=%s", (word,))
            word_id = cur.fetchone()[0]
        print("Added word", word, "with id", word_id, "to the dictionary")
        #If the word is in the vocabulary, change the level to 0 and the next review to tomorrow
        tomorrow = str((datetime.datetime.now() + datetime.timedelta(days=1)).date())
        with conn.cursor() as cur:
            cur.execute("SELECT word_id FROM "+vocab_table+" WHERE username=%s AND word_id=%s", (username, word_id))
            if cur.fetchone() is not None:
                print("Word", word, "is already in the vocabulary, resetting it now")
                cur.execute("UPDATE "+vocab_table+" SET level=0, next_review=%s WHERE username=%s AND word_id=%s", (tomorrow, username, word_id))
            #If the word is not in the vocabulary, add it with level 0 and next review tomorrow
            else:
                print("Word", word, "is not in the vocabulary, adding it now")
                cur.execute("INSERT INTO "+vocab_table+" (username, word_id, level, next_review) VALUES (%s, %s, 0, %s)", (username, word_id, tomorrow))
    class count:
        def __init__(self, conn, username):
            self.username = username
            self.conn = conn
            #Get the language from the username using user_info class
            self.language = user_info.get(self.conn, self.username).language()
        def all(self):
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM vocabulary_"+self.language+" WHERE username=%s", (self.username,))
                return cur.fetchone()[0]
        def today(self):
            #This will return the number of words that need to be reviewed today
            #These will have a next_review date of today or earlier
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM vocabulary_"+self.language+" WHERE username=%s AND next_review<=%s", (self.username, str(datetime.datetime.now().date())))
                return cur.fetchone()[0]
    class get:
        def __init__(self, conn, username):
            self.username = username
            self.conn = conn
            #Get the language from the username using user_info class
            self.language = user_info.get(self.conn, self.username).language()
        def all(self):
            #Get all words in the vocabulary
            with self.conn.cursor() as cur:
                cur.execute("SELECT word_id, level, next_review FROM vocabulary_"+self.language+" WHERE username=%s", (self.username,))
                return cur.fetchall()
        def today(self):
            #Get all words that need to be reviewed today
            with self.conn.cursor() as cur:
                cur.execute("SELECT word_id FROM vocabulary_"+self.language+" WHERE username=%s AND next_review<=%s", (self.username, str(datetime.datetime.now().date())))
                word_list = cur.fetchall()
            #Now get all the words with matching word_id from the dictionary
            words = []
            for word_id in word_list:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT word, definition, example FROM dictionary_"+self.language+" WHERE id=%s", (word_id,))
                    word_dict = {
                        "word": cur.fetchone()[0],
                        "definition": cur.fetchone()[1],
                        "example": cur.fetchone()[2]
                    }
            return words

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
import os
from urllib.parse import urlparse
from contextlib import contextmanager
import psycopg2
import random


class DataBase(object):
    def __init__(self, db_url):
        url = urlparse(os.environ[db_url])
        self.dbname = url.path[1:]
        self.user = url.username
        self.password = url.password
        self.host = url.hostname
        self.port = url.port

    @contextmanager
    def connect(self):
        connection = psycopg2.connect(dbname=self.dbname, user=self.user,
                                      password=self.password,
                                      host=self.host, port=self.port)
        yield connection
        connection.close()
    # @contextmanager
    # def connect(self):
    #     connection = psycopg2.connect(dbname='postgres', user='postgres',
    #                                   password='LF400ybk', host='localhost',
    #                                   port=5432)
    #     yield connection
    #     connection.close()

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            create table if not exists winners(
                                username varchar(200),
                                chat_id varchar(50),
                                dt date,
                                primary key (username, chat_id)
                            );
                            ''')
            cursor.execute('''
                            create table if not exists registered(
                              username varchar(200),
                              chat_id varchar(50),
                              primary key (username, chat_id) 
                            );
                            ''')
            cursor.execute('''
                            create table if not exists last_play(
                              chat_id varchar(50) primary key,
                              dt date 
                            );
                            ''')
            conn.commit()

    def get_winners_this_year(self, chat_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''select username, count(dt)
                                from winners
                                where chat_id = %s and 
                                extract(year from now()) = extract(year from dt)
                                group by username
                                order by count(dt)''', (chat_id, ))
            return cursor.fetchmany(10)

    def register_user(self, chat_id, username):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''select * from registered
                              where username = %(username)s
                               and chat_id = %(chat_id)s''',
                           {"username": username, "chat_id": chat_id})
            if cursor.fetchone() is not None:
                return False
            cursor.execute('''insert into registered
                            values(%s, %s)  
                            ''', (username, chat_id))
            conn.commit()
            return True

    def is_possible(self, chat_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''select * from last_play
                                where chat_id = %s and dt = current_date''',
                           (chat_id, ))

            if cursor.fetchone() is not None:
                return 1
            cursor.execute('''select * from registered
                                where chat_id = %s ''', (chat_id, ))
            if cursor.fetchone() is None:
                return 2
            return 0

    def choose_winner(self, chat_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''select username from registered
                                where chat_id = %s ''', (chat_id, ))
            winner_username = random.choice(cursor.fetchall())[0]
            cursor.execute('''insert into winners 
                                values (%s, %s, current_date)''', (
                winner_username,
                chat_id))
            cursor.execute('''insert into last_play
                                values (%s, current_date)
                                on conflict(chat_id) do update
                                set dt = current_date''', (chat_id, ))
            conn.commit()
            return winner_username

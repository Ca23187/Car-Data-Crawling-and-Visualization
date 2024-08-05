import sqlite3


def init_db():
    sql = '''
        create table Car
        (
            id integer primary key autoincrement, 
            brand varchar, 
            model varchar,
            price numeric,
            score numeric,
            positive_remark varchar,
            positive_score varchar,
            negative_remark varchar,
            negative_score varchar, 
            img text
        )
    '''
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


init_db()

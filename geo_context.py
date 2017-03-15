# -*- coding: utf-8 -*-
import psycopg2
from helpers.credentials import get_auth_credentials

credentials = get_auth_credentials()
conn_str = "host='localhost' dbname='twitter_context' user=" + credentials['dbuser'] + "password=" + credentials['dbpassword']

conn = psycopg2.connect(conn_str)
cur = conn.cursor()
if conn is not None:
    print("conectado")
else:
    print("fallé")


dists = range(10, 200, 10)
acts = {'IN': 'industria', 'CO': 'comercio', 'ES': 'escuelas', 'SA': 'salud',
        'OF': 'oficinas', 'OC': 'ocio', 'GO': 'gobierno'}


def append_columns_query(col):
    q_str = """alter table tweets add column %s int""" % col
    return q_str


for a in acts.keys():
    for d in dists:
        the_column = acts[a]+'_'+str(d)
        add_query = append_columns_query(the_column)
        print(add_query)
        cur.execute(add_query)
        conn.commit()

cur.close()
conn.close()

conn = psycopg2.connect(conn_str)
cur = conn.cursor()
if conn is not None:
    print("conectado")
else:
    print("fallé")


def set_query(col, buf, id_act):
    q_str = """update tweets set %s =  foo.cuantos
    from
    (
    select  t.id, count(d.id)  as cuantos
    from tweets t, denue d
    where st_dwithin(t.geom,d.geom,%d) and d.id_act like '%s'
    group by t.id) as foo
    where tweets.id = foo.id""" % (col, buf, id_act)
    return q_str


for a in acts.keys():
    for d in dists:
        the_column = acts[a]+'_'+str(d)
        s = set_query(the_column, d, a)
        print(s)
        cur.execute(s)
        conn.commit()


cur.close()
conn.close()

import sqlite3

con = sqlite3.connect(r":memory:")
cur = con.cursor()
cur.executescript("""
create table test(
    id integer primary key,
    path,
    key,
    value    
);
insert into test values(1, "bmc/0","addr","127.0.0.1");
""")
cur.execute("select * from test")
ret = cur.fetchall()
con.close()
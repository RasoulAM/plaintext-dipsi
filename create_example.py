import sqlite3
import numpy as np

conn = sqlite3.connect('example.db')
c = conn.cursor()

c.execute("CREATE TABLE table1 ( id INTEGER, val INTEGER )")
c.execute("CREATE TABLE table2 ( id INTEGER, prop INTEGER )")

A = np.random.choice(100, 10000)
B = np.random.choice(100, 10000)

for a in A:
    c.execute("INSERT INTO table1 VALUES ({},{})".format(a, a))
    
for b in B:
    c.execute("INSERT INTO table2 VALUES ({},{})".format(b, np.random.randint(0,2)))

conn.commit()
conn.close()

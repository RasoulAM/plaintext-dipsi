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


# Generate another db with table1 having 2 values for each id.
conn = sqlite3.connect('example2.db')
c = conn.cursor()

c.execute("CREATE TABLE table1 ( id INTEGER, val1 INTEGER, val2 INTEGER)")
c.execute("CREATE TABLE table2 ( id INTEGER, prop INTEGER )")
c.execute("CREATE TABLE sens ( id INTEGER, val1_sens INTEGER, val2_sens INTEGER)")

A = np.random.choice(100, 10000)
B = np.random.choice(100, 10000)

for a in A:
    c.execute("INSERT INTO table1 VALUES ({},{},{})".format(a, a, a % 10))

for b in B:
    c.execute("INSERT INTO table2 VALUES ({},{})".format(b, np.random.randint(0, 2)))

for i in range(100):
    c.execute("INSERT INTO sens VALUES ({},{},{})".format(i, 99, 9))

conn.commit()
conn.close()

#!/usr/bin/python3

import argparse
import sqlite3
from numpy.random import laplace
import numpy as np
import pandas as pd

# np.random.seed(0)

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("query_type", help="query type: 'sum' or 'count'")
parser.add_argument("db_file", help="location of sqlite database")
parser.add_argument("--eps", type=float, default=0.1, help="privacy parameter")
parser.add_argument("--t1_name", default="table1", help="name of aggregated table")
parser.add_argument("--t2_name", default="table2", help="name of second table")
parser.add_argument("--t2_params", default=[], nargs="+", help="values of prop that filter second table")
parser.add_argument("--sens", type=int, default=[], nargs="+", help="the sensitivity of each attribute")

args = parser.parse_args()
conn = sqlite3.connect(args.db_file)
c = conn.cursor()

if args.query_type == "sum":
    # estimate \Delta(table1.val) from
    # max(table1.val) * (1 + 1 / count(table1.val)) - 1
    c.execute(f"SELECT MAX(val) FROM {args.t1_name}")
    max_val, = c.fetchone()
    c.execute(f"SELECT COUNT(val) FROM {args.t1_name}")
    count_val, = c.fetchone()
    delta_val = max_val * (1 + 1 / count_val) - 1

    query = (f"SELECT SUM({args.t1_name}.val) "
             f"FROM {args.t1_name},{args.t2_name} " 
             f"WHERE {args.t1_name}.id = {args.t2_name}.id ")
    if args.t2_params:
        query += (f"AND {args.t2_name}.prop IN "
                  f"({', '.join(args.t2_params)})")
                  
    c.execute(query)
    res, = c.fetchone()
    res = res if res else 0
    res += laplace(0, delta_val / args.eps)
    print("Result of query: {:.2f}".format(res))
    
elif args.query_type == "count":
    delta_val = 1
    query = (f"SELECT COUNT({args.t1_name}.val) "
             f"FROM {args.t1_name},{args.t2_name} " 
             f"WHERE {args.t1_name}.id = {args.t2_name}.id ")
    if args.t2_params:
        query += (f"AND {args.t2_name}.prop IN "
                  f"({', '.join(args.t2_params)})")
    c.execute(query)
    res, = c.fetchone()
    res = res if res else 0
    res += laplace(0, delta_val / args.eps)
    print("Result of query: {:.2f}".format(res))

elif args.query_type == "ldp_all":
    if len(args.sens) >= 2:
        query = (f"SELECT DISTINCT {args.t1_name}.id, {args.t1_name}.val1, {args.t1_name}.val2 "
                 f"FROM {args.t1_name},{args.t2_name} "
                 f"WHERE {args.t1_name}.id = {args.t2_name}.id ")
        if args.t2_params:
            query += (f"AND {args.t2_name}.prop IN "
                      f"({', '.join(args.t2_params)})")

        c.execute(query)
        res = c.fetchall()

        for i, entry in enumerate(res):
            noise_1 = int(np.floor(laplace(0, args.sens[0] / args.eps)))  # clip the noise
            noise_2 = int(np.floor(laplace(0, args.sens[1] / args.eps)))
            new_entry = (entry[1] + noise_1, entry[2] + noise_2)
            res[i] = new_entry
        df = pd.DataFrame(res, columns=['val1', 'val2'])
        print("Result of query (first 5 lines): ")
        print(df.head())
        df.to_csv('result.csv', index=False)
    else:
        print('Require a sensitivity for every attribute.')

conn.commit()
conn.close()

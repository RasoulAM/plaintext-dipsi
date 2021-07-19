#!/usr/bin/python3

import argparse
import math
import sqlite3
from numpy.random import laplace

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("query_type", help="query type: 'sum' or 'count'")
parser.add_argument("db_file", help="location of sqlite datbase")
parser.add_argument("--eps", type=float, default=0.1, help="privacy parameter")
parser.add_argument("--t1_name", default="table1", help="name of aggregated table")
parser.add_argument("--t2_name", default="table2", help="name of second table")
parser.add_argument("--t2_params", default=[], nargs="+", help="values of prop that filter second table")

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

conn.commit()
conn.close()

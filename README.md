# Privacy-preserving Query Demonstration

This script simulates the following two queries over an SQLite database:

```
SELECT SUM(table1.val) + Laplace(0, sensitivity(SUM) / eps)
FROM table1, table2
WHERE table1.id = table2.id
AND table2.prop IN (param1, param2, ...)	
```

```
SELECT COUNT(table1.val) + Laplace(0, 1 / eps)
FROM table1, table2
WHERE table1.id = table2.id
AND table2.prop IN (param1, param2, ...)	
```

An unbiased estimate for `sensitivity(SUM)`, defined to be the maximum possible difference in `SUM` for any two tables that differ in a single entry, is obtained from the following expression:
```
MAX(table1.val)(1 + 1 / COUNT(table1.val)) - 1
```

The variance of the query results is controlled by a privacy parameter, `eps`: lower values of `eps` correspond to higher privacy but lower accuracy. Note that application-specific post-processing may be required; for instance due to the fact that the queries can return negative numbers.

## Requirements

* Python 3
* [pysqlite3](https://pypi.org/project/pysqlite3/)
* [numpy](https://pypi.org/project/numpy/)

## Usage

The script `query.py` has two required arguments, the query type (`sum` or `count`), and the location of the input database (an example input `example.db` is provided with the code).

The database is expected to have two tables, named `T1_NAME` (by default equal to `table1`) and `T2_NAME` (by default equal to `table2`). Both tables have an attribute `id`, which determines their intersection. `table1` has an attribute `val`, which determines the result of the aggregation, and `table2` has an attribute `prop`, which is used to filter the result of the intersection before aggregation. The values of `prop` on which to filter are specified by `T2_PARAMS`. If `T2_PARAMS` is not specified, no filtering is done. All table attributes are expected to be integers.

Full usage of `query.py`: 

```
usage: query.py [-h] [--eps EPS] [--t1_name T1_NAME] [--t2_name T2_NAME]
                [--t2_params T2_PARAMS [T2_PARAMS ...]]
                query_type db_file

positional arguments:
  query_type            query type: 'sum' or 'count'
  db_file               location of sqlite datbase

optional arguments:
  -h, --help            show this help message and exit
  --eps EPS             privacy parameter (default: 0.1)
  --t1_name T1_NAME     name of aggregated table (default: table1)
  --t2_name T2_NAME     name of second table (default: table2)
  --t2_params T2_PARAMS [T2_PARAMS ...]
                        values of prop that filter second table (default: [])
```

Example usage:

```
$ ./query.py sum example.db --eps 0.01 --t2_params -1 0 2
Result of query: 500821.92
```

Note that multiple runs of the same command are (intentionally and by design) not guaranteed to produce the same results due to the stochastic nature of the queries.
# Privacy-preserving Query Demonstration

This script simulates the following three queries over an SQLite database:

Sum:
```
SELECT SUM(table1.val) + Laplace(0, sensitivity(SUM) / eps)
FROM table1, table2
WHERE table1.id = table2.id
AND table1.prop IN (param1, param2, ...)	
AND table2.prop IN (param1, param2, ...)	
```
Count:
```
SELECT COUNT(table1.val) + Laplace(0, 1 / eps)
FROM table1, table2
WHERE table1.id = table2.id
AND table1.prop IN (param1, param2, ...)	
AND table2.prop IN (param1, param2, ...)	
```
ldp_all:
```
SELECT DISTINCT table1.id, table1.val1 + floor(Laplace(0, sens(table1.val1)/ eps)) , table1.val2 + floor(Laplace(0,  sens(table1.val2)/ eps))
FROM table1, table2 
WHERE table1.id = table2.id
AND table1.prop IN (param1, param2, ...)	
AND table2.prop IN (param1, param2, ...)	
```

An unbiased estimate for `sensitivity(SUM)`, defined to be the maximum possible difference in `SUM` for any two tables that differ in a single entry, is obtained from the following expression:
```
MAX(table1.val)(1 + 1 / COUNT(table1.val)) - 1
```
where `MAX(table1.val)` is the current maximum value in the table. This expression is used in the code to estimate the sensitivity.

The sensitivity for each value attribute in `table1`, for `ldp_all` can possibly be the range of values of that attribute, and are provided as input.  

The variance of the query results is controlled by a privacy parameter, `eps`: lower values of `eps` correspond to higher privacy but lower accuracy. Note that application-specific post-processing may be required; for instance due to the fact that the queries can return negative numbers.

## Requirements

* Python 3
* [pysqlite3](https://pypi.org/project/pysqlite3/)
* [numpy](https://pypi.org/project/numpy/)
* [pandas](https://pandas.pydata.org/)

## Usage

The script `query.py` has two or three required arguments depending on the query type, the arguments are query type (`sum`, `count` or `ldp_all`), the location of the input database (two example inputs `example.db` and `example2.db` are provided with the code. `example.db` used for `sum` and `count`, and `example2.db` for `ldp_all`), and finally sensitivity which typically takes two values (if you chose `ldp_all`).

For the query types `sum` and  `count`, the database is expected to have two tables, named `T1_NAME` (by default equal to `table1`) and `T2_NAME` (by default equal to `table2`). Both tables have an attribute `id`, which determines their intersection.
`table1` and `table2` both have an attribute `prop`, which is used to filter the result of the intersection before aggregation. The values of `prop` on which to filter are specified by `T1_PARAMS` and `T2_PARAMS` for the two tables, respectively. If `T1_PARAMS` or `T2_PARAMS` is not specified, no filtering is done on the corresponding table. `table1` has an attribute `val`, which determines the result of the aggregation. All table attributes are expected to be integers.

For the query type `ldp_all`, all of the above holds except for the schema of `table1`, which now has two fields that hold values `val1` and `val2`, which are returned by the query with added noise. The query only returns the first 5 entries, and the complete result is stored in `result.csv`.

Full usage of `query.py`: 

```
usage: query.py [-h] [--eps EPS] [--t1_name T1_NAME] [--t2_name T2_NAME]
                [--t1_params T1_PARAMS [T1_PARAMS ...]]
                [--t2_params T2_PARAMS [T2_PARAMS ...]]
                query_type db_file

positional arguments:
  query_type            query type: 'sum','count','ldp_all'
  db_file               location of sqlite datbase

optional arguments:
  -h, --help            show this help message and exit
  --eps EPS             privacy parameter (default: 0.1)
  --t1_name T1_NAME     name of aggregated table (default: table1)
  --t2_name T2_NAME     name of second table (default: table2)
  --t1_params T1_PARAMS [T1_PARAMS ...]
                        values of prop that filter first table (default: [])
  --t2_params T2_PARAMS [T2_PARAMS ...]
                        values of prop that filter second table (default: [])
  --sens sens1 sens2    sensitivity of val1 and val2 of table1                        
```

Example usage:

sum:
```
$ ./query.py sum example.db --eps 10 --t1_params -1 0 2 --t2_params -1 0 2
Result of query: 12260550.05
```
ldp_all:
```
$ ./query.py ldp_all example2.db --eps 10 --t1_params -1 0 2 --t2_params -1 0 2 --sens 99 9
Result of query (first 5 lines): 
   val1  val2
0    75     4
1     6     2
2     3     3
3    50     9
4    83    10
```
Note that multiple runs of the same command are (intentionally and by design) not guaranteed to produce the same results due to the stochastic nature of the queries.

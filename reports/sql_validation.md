# SQL & Reconciliation Validation

SQL files executed unchanged on a SQLite mirror of the star schema and compared with independent pandas calculations.

| check                                       |   sql_or_actual |        expected | result   |
|:--------------------------------------------|----------------:|----------------:|:---------|
| Total sales (SQL vs pandas)                 |     2.41053e+08 |     2.41053e+08 | PASS     |
| Total profit                                |     2.87976e+07 |     2.87976e+07 | PASS     |
| Distinct orders                             |  8947           |  8947           | PASS     |
| Units sold                                  | 30493           | 30493           | PASS     |
| Avg order value                             | 26942.4         | 26942.4         | PASS     |
| Top-10 products: #1 sales                   |     7.84796e+07 |     7.84796e+07 | PASS     |
| Top-10 products: same names (1=yes)         |     1           |     1           | PASS     |
| Top-10 products: sum of 10                  |     2.02503e+08 |     2.02503e+08 | PASS     |
| Months in trend (24 expected)               |    24           |    24           | PASS     |
| Monthly trend: max abs diff                 |     0           |     0           | PASS     |
| Running total last month = total            |     2.41053e+08 |     2.41053e+08 | PASS     |
| Region sales max abs diff                   |     0           |     0           | PASS     |
| Region share sums to 100                    |   100           |   100           | PASS     |
| Q5 sub-category total = total               |     2.41053e+08 |     2.41053e+08 | PASS     |
| Q8 deciles = 10                             |    10           |    10           | PASS     |
| Q8 customers in deciles                     |  1595           |  1595           | PASS     |
| Q9 matrix total = total                     |     2.41053e+08 |     2.41053e+08 | PASS     |
| Q10 bands total = total                     |     2.41053e+08 |     2.41053e+08 | PASS     |
| R3 orphan FK rows                           |     0           |     0           | PASS     |
| R4 duplicate natural keys                   |     0           |     0           | PASS     |
| R5 sales-formula violations                 |     0           |     0           | PASS     |
| Bridge total vs SQL (diff %, tolerance 0.1) |     0           |     0.1         | PASS     |

**22 / 22 checks passed.**

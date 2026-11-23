OPTIONS (SKIP=1)
LOAD DATA
INFILE 'data/clean/dim_customer.csv'
APPEND INTO TABLE dim_customer
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  customer_id,
  customer_name,
  segment,
  state
)

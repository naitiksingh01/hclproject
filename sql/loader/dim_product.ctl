OPTIONS (SKIP=1)
LOAD DATA
INFILE 'data/clean/dim_product.csv'
APPEND INTO TABLE dim_product
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  product_id,
  product_name,
  category,
  sub_category,
  list_price
)

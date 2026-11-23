OPTIONS (SKIP=1)
LOAD DATA
INFILE 'data/clean/fact_sales.csv'
APPEND INTO TABLE fact_sales
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  order_line_id,
  order_id,
  date_key,
  ship_date_key,
  customer_id,
  product_id,
  region_key,
  quantity,
  unit_price,
  discount,
  sales,
  profit,
  payment_mode,
  ship_mode,
  ship_days,
  is_bulk_order
)

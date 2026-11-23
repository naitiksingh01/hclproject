OPTIONS (SKIP=1)
LOAD DATA
INFILE 'data/clean/dim_date.csv'
APPEND INTO TABLE dim_date
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  full_date DATE 'YYYY-MM-DD',
  date_key,
  year,
  quarter,
  month_no,
  month_name,
  year_month,
  day_name,
  is_weekend
)

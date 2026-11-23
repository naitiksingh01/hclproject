OPTIONS (SKIP=1)
LOAD DATA
INFILE 'data/clean/dim_region.csv'
APPEND INTO TABLE dim_region
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  region_key,
  state,
  region
)

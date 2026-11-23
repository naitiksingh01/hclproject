# 02 – Loading the CSVs into Oracle

Two ways – use whichever you have.

## A) SQL Developer Import Wizard (easiest)
1. Right-click table (e.g. `DIM_DATE`) → **Import Data…**
2. File = `data/clean/dim_date.csv`, Header = ✔, Format = CSV.
3. For `full_date` choose Data Type **DATE** and format `YYYY-MM-DD`.
4. **Load order (FK safe):** `dim_date → dim_product → dim_customer → dim_region → fact_sales`.

## B) SQL*Loader (command line) – control files are in `sql/loader/`
```bash
sqlldr userid=USER/PASS@//localhost:1521/XEPDB1 control=sql/loader/dim_date.ctl     log=dim_date.log
sqlldr userid=USER/PASS@//localhost:1521/XEPDB1 control=sql/loader/dim_product.ctl  log=dim_product.log
sqlldr userid=USER/PASS@//localhost:1521/XEPDB1 control=sql/loader/dim_customer.ctl log=dim_customer.log
sqlldr userid=USER/PASS@//localhost:1521/XEPDB1 control=sql/loader/dim_region.ctl   log=dim_region.log
sqlldr userid=USER/PASS@//localhost:1521/XEPDB1 control=sql/loader/fact_sales.ctl   log=fact_sales.log
```
Run from the repo root so the relative `data/clean/...` paths resolve.

## After loading – verify
Run `sql/05_reconciliation.sql`. Expected: **15,181** fact rows and total sales **241,053,486.78**.

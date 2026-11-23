-- =====================================================================
-- Sales Performance Dashboard | Oracle SQL | 01 - DDL (star schema)
-- Run as the project user in SQL Developer / SQL*Plus:  @01_create_tables.sql
-- =====================================================================

-- Drop in dependency order (ignore errors on first run)
BEGIN
  FOR t IN (SELECT table_name FROM user_tables
            WHERE table_name IN ('FACT_SALES','DIM_DATE','DIM_PRODUCT','DIM_CUSTOMER','DIM_REGION')) LOOP
    EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
  END LOOP;
END;
/

CREATE TABLE dim_date (
    date_key     NUMBER(8)      CONSTRAINT pk_dim_date PRIMARY KEY,   -- YYYYMMDD
    full_date    DATE           NOT NULL,
    year         NUMBER(4)      NOT NULL,
    quarter      VARCHAR2(2)    NOT NULL,
    month_no     NUMBER(2)      NOT NULL,
    month_name   VARCHAR2(3)    NOT NULL,
    year_month   VARCHAR2(7)    NOT NULL,                              -- e.g. 2024-03
    day_name     VARCHAR2(3)    NOT NULL,
    is_weekend   NUMBER(1)      CONSTRAINT ck_dd_wkend CHECK (is_weekend IN (0,1))
);

CREATE TABLE dim_product (
    product_id    VARCHAR2(10)  CONSTRAINT pk_dim_product PRIMARY KEY,
    product_name  VARCHAR2(80)  NOT NULL,
    category      VARCHAR2(40)  NOT NULL,
    sub_category  VARCHAR2(40)  NOT NULL,
    list_price    NUMBER(12,2)  CONSTRAINT ck_dp_price CHECK (list_price > 0)
);

CREATE TABLE dim_customer (
    customer_id    VARCHAR2(10) CONSTRAINT pk_dim_customer PRIMARY KEY,
    customer_name  VARCHAR2(80) NOT NULL,
    segment        VARCHAR2(20),
    state          VARCHAR2(40)
);

CREATE TABLE dim_region (
    region_key  NUMBER(3)       CONSTRAINT pk_dim_region PRIMARY KEY,
    state       VARCHAR2(40)    NOT NULL,
    region      VARCHAR2(20)    NOT NULL
);

CREATE TABLE fact_sales (
    order_line_id  NUMBER(10)   CONSTRAINT pk_fact_sales PRIMARY KEY,
    order_id       VARCHAR2(20) NOT NULL,
    date_key       NUMBER(8)    NOT NULL CONSTRAINT fk_fs_date  REFERENCES dim_date(date_key),
    ship_date_key  NUMBER(8)    NOT NULL CONSTRAINT fk_fs_ship  REFERENCES dim_date(date_key),
    customer_id    VARCHAR2(10) NOT NULL CONSTRAINT fk_fs_cust  REFERENCES dim_customer(customer_id),
    product_id     VARCHAR2(10) NOT NULL CONSTRAINT fk_fs_prod  REFERENCES dim_product(product_id),
    region_key     NUMBER(3)    NOT NULL CONSTRAINT fk_fs_reg   REFERENCES dim_region(region_key),
    quantity       NUMBER(5)    NOT NULL CONSTRAINT ck_fs_qty   CHECK (quantity > 0),
    unit_price     NUMBER(12,2) NOT NULL CONSTRAINT ck_fs_price CHECK (unit_price > 0),
    discount       NUMBER(3,2)  NOT NULL CONSTRAINT ck_fs_disc  CHECK (discount BETWEEN 0 AND 1),
    sales          NUMBER(14,2) NOT NULL CONSTRAINT ck_fs_sales CHECK (sales >= 0),
    profit         NUMBER(14,2),
    payment_mode   VARCHAR2(20),
    ship_mode      VARCHAR2(20),
    ship_days      NUMBER(3),
    is_bulk_order  NUMBER(1)    DEFAULT 0
);

CREATE INDEX ix_fs_date   ON fact_sales(date_key);
CREATE INDEX ix_fs_prod   ON fact_sales(product_id);
CREATE INDEX ix_fs_cust   ON fact_sales(customer_id);
CREATE INDEX ix_fs_region ON fact_sales(region_key);

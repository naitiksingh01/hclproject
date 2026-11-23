# Data-Quality Report

Source: `data/raw/retail_sales_raw.csv` (15,610 rows, 20 columns) → cleaned by `python/02_clean_sales.py`.
All counts below are produced by the script and stored in `reports/dq_summary.json`.

## 1. Issues found and the rule applied
| ID | Issue | Rows | Rule / decision |
|---|---|---:|---|
| R1 | Exact duplicate rows | 276 | Removed (kept first); listed in `duplicates_removed.csv` |
| R2 | Region text inconsistent (UPPER-case / leading-trailing spaces) | 756 | Trim + standardise |
| R3 | Region null | 230 | Re-derived from `state` (state→region master); 0 unknown remain |
| R4 | Product name null | 92 | Recovered from `product_id` master; category/sub-category also taken from master (fixes lower-case categories) |
| R5a | Non-ISO date strings (`dd/mm/yyyy`, `Mon dd, yyyy`) | 967 (incl. 61 invalid) | Parsed with explicit formats → `YYYY-MM-DD` |
| R5b | Impossible date (`31-02-2023`) | 61 | Quarantined (`INVALID_ORDER_DATE`) |
| R6 | Negative sales / quantity (refund-type entries) | 92 | Quarantined (`NEGATIVE_AMOUNT_REFUND_ENTRY`), excluded from sales |
| R7 | Discount null | 122 | Inferred from sales ÷ (qty × price), snapped to valid discount grid |
| R8 | `sales` ≠ qty × price × (1 − discount) | 143 | Recomputed; net adjustment ₹ −2,286 on corrected rows |
| R9 | Customer ID null | 179 | Kept, assigned `UNKNOWN` (revenue is real); excluded from customer counts |
| R10 | Quantity outliers (qty ≥ 40, bulk orders) | 23 | Kept, flagged `is_bulk_order = 1` |

Null counts before: customer_id 188, region 236, discount 124, product_name 92 → **after cleaning: 0 nulls in all columns.**

## 2. Row & value reconciliation (raw → clean)
| Step | Amount (₹) |
|---|---:|
| Raw file total, as received | 245,741,745.95 |
| less: exact duplicate rows | −4,248,593.54 |
| less: invalid-date rows | −542,585.31 |
| less: negative / refund rows (removing negatives *adds back*) | +1,412,590.24 |
| adjust: sales recomputed | −33,253.05 |
| **Clean total** | **241,053,486.78** |

Bridge difference vs clean fact table: **₹ 0.00** (acceptance: within 0.1 %). Rows: 15,610 − 276 − 61 − 92 = **15,181** (validated: 15,181 in fact table).

## 3. Three-way reconciliation (CSV ↔ Oracle ↔ Power BI)
| Metric | Python (clean CSV) | Oracle SQL | Power BI (DAX) |
|---|---:|---:|---:|
| Fact rows | 15,181 | 15,181 | 15,181 (row count of `fact_sales`) |
| Total sales | 241,053,486.78 | 241,053,486.78 | must show ₹24.11 Cr / 241,053,486.78 |
| Orders | 8,947 | 8,947 | 8,947 |

Python ↔ SQL equality is proven by `python/03_validate_sql.py` (22/22 checks, `reports/sql_validation.md`). Fill the Power BI column from your own report after loading (`powerbi/POWERBI_BUILD_GUIDE.md`, step 8).

## 4. Integrity checks after cleaning
Orphan foreign keys = 0 · duplicate natural keys = 0 · sales-formula violations = 0 · ship_date ≥ order_date for all rows.

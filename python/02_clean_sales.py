"""
02_clean_sales.py  -  Cleaning + star-schema build for the Sales Performance Dashboard.

Input : data/raw/retail_sales_raw.csv
Output: data/clean/*.csv  (star schema)  +  data/powerbi/*.csv (same, Power BI load folder)
        reports/dq_summary.json, reports/rejected_rows.csv, reports/duplicates_removed.csv,
        reports/reconciliation_bridge.csv
Every rule is logged with the number of rows it touched -> feeds the Data-Quality Report.
"""
import json, shutil
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW  = ROOT/"data/raw/retail_sales_raw.csv"
CLEAN= ROOT/"data/clean"; PBI = ROOT/"data/powerbi"; REP = ROOT/"reports"
for p in (CLEAN,PBI,REP): p.mkdir(parents=True,exist_ok=True)

log = {}                                   # rule -> rows affected
raw = pd.read_csv(RAW, dtype=str)
log["raw_rows"] = len(raw)
for c in ["quantity","unit_price","discount","sales","profit"]:
    raw[c] = pd.to_numeric(raw[c], errors="coerce")
raw_total = raw["sales"].sum()
log["raw_total_sales"] = round(raw_total,2)

# profile of problems BEFORE fixing (for the report)
log["null_counts_before"] = raw.isna().sum()[lambda s: s>0].to_dict()
log["negative_sales_rows"] = int((raw.sales<0).sum())

df = raw.copy()
df["source_row"] = np.arange(2, len(df)+2)          # CSV line number for traceability

# ---- R1 exact duplicates ---------------------------------------------------
dup_mask = df.duplicated(subset=[c for c in df.columns if c!="source_row"], keep="first")
dups = df[dup_mask].copy(); dups["reason"]="EXACT_DUPLICATE"
df = df[~dup_mask].copy(); log["R1_exact_duplicates_removed"]=len(dups)

# ---- R2 text standardisation ----------------------------------------------
for c in ["region","state","category","sub_category","product_name","customer_name","segment","payment_mode","ship_mode"]:
    df[c] = df[c].astype("string").str.strip().str.replace(r"\s+"," ",regex=True)
log["R2_region_case_or_space_fixed"] = int((df.region.notna() & (df.region != df.region.str.title())).sum()
                                           + df.region.str.contains(r"^\s|\s$",na=False).sum())
df["category"]=df["category"].str.title().replace({"Home & Kitchen":"Home & Kitchen"})
df["state"]=df["state"].str.title()

# ---- R3 region derived from state (fixes nulls + case issues) --------------
state_region = {"Delhi":"North","Uttar Pradesh":"North","Punjab":"North","Haryana":"North",
 "Karnataka":"South","Tamil Nadu":"South","Kerala":"South","Telangana":"South",
 "West Bengal":"East","Odisha":"East","Bihar":"East","Assam":"East",
 "Maharashtra":"West","Gujarat":"West","Rajasthan":"West","Goa":"West",
 "Madhya Pradesh":"Central","Chhattisgarh":"Central"}
before_null = df.region.isna().sum()
df["region"] = df["state"].map(state_region)
log["R3_region_nulls_recovered_from_state"] = int(before_null)
log["R3_region_still_unknown"] = int(df.region.isna().sum())

# ---- R4 product attributes recovered from product_id -----------------------
pmap = (df.dropna(subset=["product_name"]).groupby("product_id")[["product_name","category","sub_category"]]
          .agg(lambda s: s.mode().iloc[0]))
miss = df.product_name.isna()
df.loc[miss,"product_name"] = df.loc[miss,"product_id"].map(pmap["product_name"])
df["category"]    = df["product_id"].map(pmap["category"])      # master value wins (fixes lower-case)
df["sub_category"]= df["product_id"].map(pmap["sub_category"])
log["R4_product_name_recovered"] = int(miss.sum())

# ---- R5 dates --------------------------------------------------------------
def parse_date(s):
    for fmt in ("%Y-%m-%d","%d/%m/%Y","%b %d, %Y"):
        try: return pd.to_datetime(s, format=fmt)
        except Exception: pass
    return pd.NaT
log["R5_multi_format_dates_standardised"]=int((~df.order_date.str.match(r"^\d{4}-\d{2}-\d{2}$",na=False)).sum())
df["order_date"]=df["order_date"].map(parse_date)
df["ship_date"] =df["ship_date"].map(parse_date)
bad_date = df.order_date.isna()
rej_date = df[bad_date].copy(); rej_date["reason"]="INVALID_ORDER_DATE"
df = df[~bad_date].copy(); log["R5_invalid_dates_rejected"]=len(rej_date)

# ---- R6 negative / refund amounts -> quarantine ----------------------------
neg = (df.sales<0)|(df.quantity<=0)
rej_neg = df[neg].copy(); rej_neg["reason"]="NEGATIVE_AMOUNT_REFUND_ENTRY"
df = df[~neg].copy(); log["R6_negative_amount_rejected"]=len(rej_neg)

# ---- R7 discount nulls: infer from sales, snap to valid grid ---------------
grid = np.array([0,.05,.10,.15,.20,.30])
implied = 1 - df.sales/(df.quantity*df.unit_price)
snap = pd.Series(grid[np.abs(implied.values[:,None]-grid[None,:]).argmin(1)], index=df.index)
ok = (np.abs(implied-snap)<0.006)
m = df.discount.isna()
df.loc[m & ok,"discount"]=snap[m & ok]
df.loc[m & ~ok,"discount"]=0.0
log["R7_discount_nulls_filled"]=int(m.sum()); log["R7_of_which_default_zero"]=int((m & ~ok).sum())

# ---- R8 recompute sales = qty*price*(1-disc) -------------------------------
expected = (df.quantity*df.unit_price*(1-df.discount)).round(2)
wrong = (np.abs(df.sales-expected) > 0.01*expected.abs()+0.02)
log["R8_sales_total_mismatch_corrected"]=int(wrong.sum())
log["R8_sales_adjustment_value"]=round(float((expected[wrong]-df.sales[wrong]).sum()),2)  # corrected rows only
df["sales_reported"]=df["sales"]
df["sales"]=expected

# ---- R9 customer nulls -> 'UNKNOWN' (kept, flagged) ------------------------
log["R9_customer_id_null_flagged"]=int(df.customer_id.isna().sum())
df["customer_id"]=df.customer_id.fillna("UNKNOWN")
df["customer_name"]=df.customer_name.fillna("Unknown Customer")
df.loc[df.customer_id=="UNKNOWN","customer_name"]="Unknown Customer"
# one name per customer_id (mode)
nm = df[df.customer_id!="UNKNOWN"].groupby("customer_id")["customer_name"].agg(lambda s:s.mode().iloc[0])
df.loc[df.customer_id!="UNKNOWN","customer_name"]=df.customer_id.map(nm)

# ---- R10 outliers: flag, do not delete (legit bulk orders) -----------------
df["is_bulk_order"]=(df.quantity>=40).astype(int)
log["R10_bulk_order_outliers_flagged_kept"]=int(df.is_bulk_order.sum())

# ---- R11 integrity -----------------------------------------------------
assert df.ship_date.ge(df.order_date).all(), "ship before order"
# profit kept from source; scale it where sales had to be corrected so margin stays consistent
df["profit"]=(df.profit*(df.sales/df.sales_reported)).round(2)
df["order_line_id"]=range(1,len(df)+1)
log["clean_rows"]=len(df); log["clean_total_sales"]=round(float(df.sales.sum()),2)

# ---------- reconciliation bridge raw -> clean -------------------------------
bridge = [("Raw file total (as received)",raw_total),
          ("less: exact duplicate rows",-dups.sales.sum()),
          ("less: invalid-date rows",-rej_date.sales.sum()),
          ("less: negative/refund rows",-rej_neg.sales.sum()),
          ("adjust: sales recomputed (qty x price x (1-disc))", df.sales.sum()-df.sales_reported.sum())]
bd = pd.DataFrame(bridge,columns=["step","amount"]); bd["amount"]=bd.amount.round(2)
bd.loc[len(bd)]=["Clean total (= sum of steps)",bd.amount.sum().round(2)]
assert abs(bd.amount.iloc[-1]-df.sales.sum())<1, (bd.amount.iloc[-1],df.sales.sum())
bd.to_csv(REP/"reconciliation_bridge.csv",index=False)
log["reconciliation_diff_vs_clean"]=round(float(bd.amount.iloc[-1]-df.sales.sum()),2)

pd.concat([dups,rej_date,rej_neg])[["source_row","order_id","order_date","customer_id","product_id","quantity","sales","reason"]]\
  .to_csv(REP/"rejected_rows.csv",index=False)
dups.to_csv(REP/"duplicates_removed.csv",index=False)

# ---------- star schema ---------------------------------------------------
dim_date = pd.DataFrame({"date":pd.date_range(df.order_date.min().replace(day=1),"2024-12-31")})
dim_date["date_key"]=dim_date.date.dt.strftime("%Y%m%d").astype(int)
dim_date["year"]=dim_date.date.dt.year; dim_date["quarter"]="Q"+dim_date.date.dt.quarter.astype(str)
dim_date["month_no"]=dim_date.date.dt.month; dim_date["month_name"]=dim_date.date.dt.strftime("%b")
dim_date["year_month"]=dim_date.date.dt.strftime("%Y-%m"); dim_date["day_name"]=dim_date.date.dt.strftime("%a")
dim_date["is_weekend"]=(dim_date.date.dt.dayofweek>=5).astype(int)
dim_date["date"]=dim_date.date.dt.strftime("%Y-%m-%d")

dim_product=(df.groupby("product_id").agg(product_name=("product_name","first"),category=("category","first"),
             sub_category=("sub_category","first"),list_price=("unit_price","median")).round(2).reset_index())
dim_customer=(df.groupby("customer_id").agg(customer_name=("customer_name","first"),segment=("segment","first"),
             state=("state","first")).reset_index())
dim_region=pd.DataFrame(sorted(state_region.items()),columns=["state","region"])
dim_region.insert(0,"region_key",range(1,len(dim_region)+1))
fact=df.copy()
fact["date_key"]=fact.order_date.dt.strftime("%Y%m%d").astype(int)
fact["ship_date_key"]=fact.ship_date.dt.strftime("%Y%m%d").astype(int)
fact["region_key"]=fact.state.map(dim_region.set_index("state")["region_key"])
fact["ship_days"]=(fact.ship_date-fact.order_date).dt.days
fact=fact[["order_line_id","order_id","date_key","ship_date_key","customer_id","product_id","region_key",
           "quantity","unit_price","discount","sales","profit","payment_mode","ship_mode","ship_days","is_bulk_order"]]
for name,t in {"fact_sales":fact,"dim_date":dim_date,"dim_product":dim_product,"dim_customer":dim_customer,"dim_region":dim_region}.items():
    t.to_csv(CLEAN/f"{name}.csv",index=False); t.to_csv(PBI/f"{name}.csv",index=False)
# flat version for quick tools
flat=df[["order_line_id","order_id","order_date","ship_date","customer_id","customer_name","segment","product_id","product_name",
         "category","sub_category","state","region","quantity","unit_price","discount","sales","profit","payment_mode","ship_mode","is_bulk_order"]].copy()
flat["order_date"]=flat.order_date.dt.strftime("%Y-%m-%d"); flat["ship_date"]=flat.ship_date.dt.strftime("%Y-%m-%d")
flat.to_csv(CLEAN/"sales_clean_flat.csv",index=False)
log["null_counts_after"]=flat.isna().sum()[lambda s:s>0].to_dict()
json.dump(log,open(REP/"dq_summary.json","w"),indent=2,default=str)
print(json.dumps(log,indent=2,default=str)); print(bd)

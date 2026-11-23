"""
03_validate_sql.py - proves the SQL logic and the three-way reconciliation.
Oracle is not available in every environment, so the same star schema is loaded into SQLite
and sql/03_views.sql + sql/04_analysis_queries.sql are executed UNCHANGED (only
'CREATE OR REPLACE VIEW' -> 'CREATE VIEW'). Results are compared with independent pandas maths.
Writes reports/sql_validation.md
"""
import re, sqlite3, sys
from pathlib import Path
import pandas as pd, numpy as np
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/"data/clean"
con=sqlite3.connect(":memory:")
for t in ["dim_date","dim_product","dim_customer","dim_region","fact_sales"]:
    pd.read_csv(C/f"{t}.csv").to_sql(t,con,index=False)
def run_file(path):
    txt=re.sub(r"--[^\n]*","",path.read_text()).replace("CREATE OR REPLACE VIEW","CREATE VIEW")
    return [s.strip() for s in txt.split(";") if s.strip()]
for s in run_file(ROOT/"sql/03_views.sql"): con.execute(s)
qs=run_file(ROOT/"sql/04_analysis_queries.sql"); res={f"Q{i+1}":pd.read_sql(q,con) for i,q in enumerate(qs)}

flat=pd.read_csv(C/"sales_clean_flat.csv",parse_dates=["order_date"])
flat["ym"]=flat.order_date.dt.strftime("%Y-%m")
checks=[]
def chk(name,a,b,tol=0.005):
    ok=abs(a-b)<=tol; checks.append((name,a,b,"PASS" if ok else "FAIL")); return ok
k=res["Q1"].iloc[0]
chk("Total sales (SQL vs pandas)",k.total_sales,round(flat.sales.sum(),2))
chk("Total profit",k.total_profit,round(flat.profit.sum(),2))
chk("Distinct orders",k.total_orders,flat.order_id.nunique())
chk("Units sold",k.units_sold,flat.quantity.sum())
chk("Avg order value",k.avg_order_value,round(flat.sales.sum()/flat.order_id.nunique(),2))
top=flat.groupby("product_name").sales.sum().sort_values(ascending=False).head(10)
chk("Top-10 products: #1 sales",res["Q2"].total_sales.iloc[0],round(top.iloc[0],2))
chk("Top-10 products: same names (1=yes)",float(set(res["Q2"].product_name)==set(top.index)),1.0)
chk("Top-10 products: sum of 10",round(res["Q2"].total_sales.sum(),2),round(top.sum(),2))
m=flat.groupby("ym").sales.sum().round(2)
chk("Months in trend (24 expected)",len(res["Q3"]),len(m),0)
chk("Monthly trend: max abs diff",float((res["Q3"].set_index("year_month").monthly_sales-m).abs().max()),0.0)
chk("Running total last month = total",res["Q3"].running_total.iloc[-1],round(flat.sales.sum(),2),0.01)
r=flat.groupby("region").sales.sum().round(2)
chk("Region sales max abs diff",float((res["Q4"].set_index("region").total_sales-r).abs().max()),0.0)
chk("Region share sums to 100",round(res["Q4"].sales_share_pct.sum(),1),100.0,0.1)
chk("Q5 sub-category total = total",round(res["Q5"].total_sales.sum(),2),round(flat.sales.sum(),2),0.05)
chk("Q8 deciles = 10",len(res["Q8"]),10,0)
chk("Q8 customers in deciles",res["Q8"].customers.sum(),flat[flat.customer_id!="UNKNOWN"].customer_id.nunique(),0)
chk("Q9 matrix total = total",round(res["Q9"].iloc[:,1:].sum().sum(),2),round(flat.sales.sum(),2),0.05)
chk("Q10 bands total = total",round(res["Q10"].total_sales.sum(),2),round(flat.sales.sum(),2),0.05)
# data-quality gates from reconciliation file
chk("R3 orphan FK rows",int(pd.read_sql("SELECT COUNT(*) n FROM fact_sales f LEFT JOIN dim_product p ON p.product_id=f.product_id LEFT JOIN dim_customer c ON c.customer_id=f.customer_id LEFT JOIN dim_region r ON r.region_key=f.region_key WHERE p.product_id IS NULL OR c.customer_id IS NULL OR r.region_key IS NULL",con).n[0]),0,0)
chk("R4 duplicate natural keys",len(pd.read_sql("SELECT 1 FROM fact_sales GROUP BY order_id,product_id,date_key,customer_id,quantity,unit_price HAVING COUNT(*)>1",con)),0,0)
chk("R5 sales-formula violations",len(pd.read_sql("SELECT 1 FROM fact_sales WHERE ABS(sales-ROUND(quantity*unit_price*(1-discount),2))>0.02",con)),0,0)
# 0.1% tolerance vs raw-to-clean bridge
bridge=pd.read_csv(ROOT/"reports/reconciliation_bridge.csv")
exp=bridge.amount.iloc[:-1].sum(); diff=abs(k.total_sales-exp)/exp*100
checks.append(("Bridge total vs SQL (diff %, tolerance 0.1)",round(diff,6),0.1,"PASS" if diff<0.1 else "FAIL"))

out=pd.DataFrame(checks,columns=["check","sql_or_actual","expected","result"])
md=["# SQL & Reconciliation Validation\n",
    "SQL files executed unchanged on a SQLite mirror of the star schema and compared with independent pandas calculations.\n",
    out.to_markdown(index=False) if hasattr(out,"to_markdown") else out.to_string(index=False),
    f"\n**{(out.result=='PASS').sum()} / {len(out)} checks passed.**\n"]
(ROOT/"reports/sql_validation.md").write_text("\n".join(md))
# save query outputs for the dashboard / report
for n,d in res.items(): d.to_csv(ROOT/"reports"/f"sql_output_{n}.csv",index=False)
print(out.to_string(index=False)); sys.exit(0 if (out.result=="PASS").all() else 1)

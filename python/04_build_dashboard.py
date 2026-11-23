"""04_build_dashboard.py - builds dashboard/sales_dashboard.html (self-contained, no internet needed).
A browser-based replica of the Power BI report: KPI cards, 3 slicers, cross-filtering, drill-down."""
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
f=pd.read_csv(ROOT/"data/clean/sales_clean_flat.csv",parse_dates=["order_date"])
f["ym"]=f.order_date.dt.strftime("%Y-%m")
cols=["ym","region","category","sub_category","product_name","segment","payment_mode"]
dic={c:sorted(f[c].unique()) for c in cols}
oid={o:i for i,o in enumerate(f.order_id.unique())}
cid={o:i for i,o in enumerate(f.customer_id.unique())}
rows=[[dic[c].index(getattr(r,c)) for c in cols]+[round(r.sales),round(r.profit),int(r.quantity),oid[r.order_id],cid[r.customer_id],1 if r.customer_id=="UNKNOWN" else 0]
      for r in f.itertuples()]
data=json.dumps({"dic":dic,"cols":cols,"rows":rows},separators=(",",":"))
html=(ROOT/"python/dashboard_template.html").read_text().replace("/*__DATA__*/null",data)
(ROOT/"dashboard").mkdir(exist_ok=True)
(ROOT/"dashboard/sales_dashboard.html").write_text(html)
print("dashboard size KB:",len(html)//1024)

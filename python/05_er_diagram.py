import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path
out=Path(__file__).resolve().parents[1]/"docs/er_star_schema.png"
T={"FACT_SALES":(5.2,1.5,["PK order_line_id","order_id","FK date_key","FK ship_date_key","FK customer_id","FK product_id","FK region_key","quantity","unit_price","discount","sales","profit","payment_mode","ship_mode","ship_days","is_bulk_order"],"#2f6fed"),
"DIM_DATE":(0.3,5.8,["PK date_key","full_date","year","quarter","month_no","month_name","year_month","day_name","is_weekend"],"#12a594"),
"DIM_PRODUCT":(10.3,7.4,["PK product_id","product_name","category","sub_category","list_price"],"#12a594"),
"DIM_CUSTOMER":(0.3,1.2,["PK customer_id","customer_name","segment","state"],"#12a594"),
"DIM_REGION":(10.3,2.2,["PK region_key","state","region"],"#12a594")}
fig,ax=plt.subplots(figsize=(14,9)); ax.set_xlim(0,14); ax.set_ylim(0,12); ax.axis("off")
box={}
for n,(x,y,cols,c) in T.items():
    h=0.45*(len(cols)+1); w=3.4 if n!="FACT_SALES" else 3.6
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02",fc="white",ec=c,lw=2))
    ax.add_patch(FancyBboxPatch((x,y+h-0.45),w,0.45,boxstyle="round,pad=0.02",fc=c,ec=c))
    ax.text(x+w/2,y+h-0.23,n,ha="center",va="center",color="white",fontweight="bold",fontsize=11)
    for i,t in enumerate(cols): ax.text(x+0.15,y+h-0.45-0.4*(i+1)+0.1,t,fontsize=9,fontweight="bold" if t.startswith(("PK","FK")) else "normal",va="center")
    box[n]=(x,y,w,h)
def link(xa,ya,xb,yb): ax.annotate("",xy=(xb,yb),xytext=(xa,ya),arrowprops=dict(arrowstyle="-|>",color="#555",lw=1.4))
fx,fy,fh=5.2,1.5,0.45*17
for n,side in [("DIM_DATE","L"),("DIM_CUSTOMER","L"),("DIM_PRODUCT","R"),("DIM_REGION","R")]:
    x,y,w,h=box[n]; sx=x+w if side=="L" else x
    link(sx,y+h/2,fx if side=="L" else fx+3.6,{"DIM_DATE":fy+fh-1.3,"DIM_CUSTOMER":fy+4.0,"DIM_PRODUCT":fy+fh-1.3,"DIM_REGION":fy+4.0}[n])
ax.text(7,11.5,"Star schema - Sales Performance Dashboard (1 fact, 4 dimensions)",ha="center",fontsize=14,fontweight="bold")
ax.text(7,0.3,"Arrows: dimension (1)  ->  fact (many). dim_date is used twice: order date and ship date.",ha="center",fontsize=10,color="#555")
plt.savefig(out,dpi=150,bbox_inches="tight"); print(out)

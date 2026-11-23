"""
01_generate_dataset.py
Generates a realistic, intentionally DIRTY retail sales CSV (Kaggle "Superstore"-style).
Synthetic data (seeded -> reproducible). Dirty patterns injected on purpose so the
cleaning pipeline and data-quality report have real work to do:
  * exact duplicate rows            * null customer / region
  * negative amounts (refund rows)  * mixed date formats / impossible dates
  * inconsistent text (case/space)  * wrong 'sales' totals
"""
import numpy as np, pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "retail_sales_raw.csv"

catalog = {
 "Technology":      {"Phones":[("Smartphone X1",18000),("Smartphone Lite",9500),("Phone Case Pro",450)],
                     "Accessories":[("Wireless Mouse",650),("Mech Keyboard",2400),("USB-C Hub",1300),("Bluetooth Speaker",2200)],
                     "Computers":[("Laptop Air 14",52000),("Laptop Pro 16",89000),("Monitor 24in",11500)]},
 "Furniture":       {"Chairs":[("Ergo Chair",8200),("Task Chair",4300),("Gaming Chair",9800)],
                     "Tables":[("Office Desk",7600),("Standing Desk",15500),("Coffee Table",3900)],
                     "Storage":[("Bookcase",5200),("File Cabinet",3600)]},
 "Office Supplies": {"Paper":[("A4 Paper Ream",320),("Sticky Notes",90),("Notebook Pack",240)],
                     "Binders":[("Ring Binder",140),("Box File",210)],
                     "Art & Stationery":[("Gel Pen Box",180),("Marker Set",260),("Stapler",170)]},
 "Home & Kitchen":  {"Appliances":[("Air Fryer",6200),("Mixer Grinder",3800),("Electric Kettle",1500),("Microwave Oven",9800)],
                     "Cookware":[("Non-stick Pan",1100),("Pressure Cooker",2100)]},
 "Fashion":         {"Footwear":[("Running Shoes",3200),("Formal Shoes",2800),("Sandals",900)],
                     "Apparel":[("Cotton T-Shirt",600),("Denim Jeans",1800),("Winter Jacket",3600)]},
 "Sports":          {"Equipment":[("Cricket Bat",2600),("Yoga Mat",800),("Dumbbell Set",2900),("Football",950)]},
}
products=[]; pid=1000
for cat,subs in catalog.items():
    for sub,items in subs.items():
        for name,price in items:
            pid+=1; products.append((f"P{pid}",name,cat,sub,price))
prod=pd.DataFrame(products,columns=["product_id","product_name","category","sub_category","base_price"])

regions={"North":["Delhi","Uttar Pradesh","Punjab","Haryana"],
         "South":["Karnataka","Tamil Nadu","Kerala","Telangana"],
         "East":["West Bengal","Odisha","Bihar","Assam"],
         "West":["Maharashtra","Gujarat","Rajasthan","Goa"],
         "Central":["Madhya Pradesh","Chhattisgarh"]}
reg_w={"North":.27,"South":.26,"East":.14,"West":.25,"Central":.08}
state_to_reg={s:r for r,ss in regions.items() for s in ss}

first=["Aarav","Vivaan","Aditya","Ananya","Diya","Ishaan","Kavya","Rohan","Saanvi","Arjun","Meera","Kabir","Neha","Rahul","Priya","Sneha","Vikram","Pooja","Amit","Sakshi"]
last=["Sharma","Verma","Singh","Gupta","Patel","Reddy","Nair","Das","Joshi","Mehta","Iyer","Khan","Bhadoriya","Yadav","Chauhan"]
N_CUST=1600
cust=pd.DataFrame({"customer_id":[f"C{10000+i}" for i in range(N_CUST)],
    "customer_name":[f"{rng.choice(first)} {rng.choice(last)}" for _ in range(N_CUST)]})
cust["state"]=rng.choice(list(state_to_reg),N_CUST,p=None)
# weight states by region weight
st=list(state_to_reg); w=np.array([reg_w[state_to_reg[s]]/len(regions[state_to_reg[s]]) for s in st]); w/=w.sum()
cust["state"]=rng.choice(st,N_CUST,p=w)
cust["segment"]=rng.choice(["Consumer","Corporate","Home Office"],N_CUST,p=[.55,.30,.15])

BASE_M={"Technology":.13,"Furniture":.16,"Office Supplies":.30,"Home & Kitchen":.20,"Fashion":.34,"Sports":.24}
N_ORD=9000
days=pd.date_range("2023-01-01","2024-12-31")
# seasonality: festive (Oct-Nov), year-end bump, growth in 2024
dw=np.array([1+0.55*(d.month in (10,11))+0.25*(d.month==12)+0.12*(d.year==2024)+0.1*(d.dayofweek>=5) for d in days]); dw/=dw.sum()
order_dates=rng.choice(days,N_ORD,p=dw)
rows=[]
pw=np.linspace(1.8,0.6,len(prod)); pw/=pw.sum()
for i in range(N_ORD):
    c=cust.iloc[rng.integers(0,N_CUST)]
    od=pd.Timestamp(order_dates[i])
    for _ in range(rng.choice([1,2,3,4],p=[.55,.25,.14,.06])):
        p=prod.iloc[rng.choice(len(prod),p=pw)]
        qty=int(rng.choice([1,2,3,4,5],p=[.5,.25,.13,.08,.04]))
        price=round(p.base_price*rng.uniform(.95,1.08),2)
        disc=float(rng.choice([0,0,0,.05,.10,.15,.20,.30],p=[.3,.2,.1,.1,.1,.08,.07,.05]))
        sales=round(qty*price*(1-disc),2)
        margin=BASE_M[p.category]-0.55*disc+rng.normal(0,0.03)      # deeper discount -> thinner margin
        profit=round(sales*margin,2)
        rows.append([f"ORD-{od.year}-{100000+i}",od,c.customer_id,c.customer_name,c.state,
                     p.product_id,p.product_name,p.category,p.sub_category,qty,price,disc,sales,profit,
                     rng.choice(["UPI","Credit Card","Debit Card","Net Banking","COD"],p=[.38,.2,.17,.1,.15]),
                     rng.choice(["Standard","Express","Same Day"],p=[.6,.3,.1])])
df=pd.DataFrame(rows,columns=["order_id","order_date","customer_id","customer_name","state","product_id",
    "product_name","category","sub_category","quantity","unit_price","discount","sales","profit","payment_mode","ship_mode"])
df["region"]=df["state"].map(state_to_reg)
df["segment"]=df["customer_id"].map(cust.set_index("customer_id")["segment"])
df["ship_date"]=df["order_date"]+pd.to_timedelta(rng.choice([1,2,3,4,5,6,7],len(df),p=[.1,.2,.25,.2,.12,.08,.05]),unit="D")

# ---------- inject dirt ----------
n=len(df)
def pick(frac): return rng.choice(n,int(n*frac),replace=False)
# date formats
od=df["order_date"].dt.strftime("%Y-%m-%d").astype(object)
sd=df["ship_date"].dt.strftime("%Y-%m-%d").astype(object)
i1=pick(.04); od.iloc[i1]=df["order_date"].iloc[i1].dt.strftime("%d/%m/%Y")
i2=pick(.02); od.iloc[i2]=df["order_date"].iloc[i2].dt.strftime("%b %d, %Y")
i3=pick(.004); od.iloc[i3]=["31-02-2023"]*len(i3)            # impossible date
i3b=pick(.003); sd.iloc[i3b]=df["order_date"].iloc[i3b].dt.strftime("%Y-%m-%d")  # ship == order ok
df["order_date"]=od; df["ship_date"]=sd
# nulls
df.loc[pick(.012),"customer_id"]=np.nan
df.loc[pick(.015),"region"]=np.nan
df.loc[pick(.008),"discount"]=np.nan
df.loc[pick(.006),"product_name"]=np.nan
# text inconsistency
j=pick(.05); df.loc[j,"region"]=df.loc[j,"region"].astype(str).str.upper()
j=pick(.04); df.loc[j,"region"]=" "+df.loc[j,"region"].astype(str)+" "
j=pick(.03); df.loc[j,"category"]=df.loc[j,"category"].str.lower()
# negative amounts (refund-like)
j=pick(.006); df.loc[j,"sales"]=-df.loc[j,"sales"].abs(); df.loc[j,"quantity"]=-df.loc[j,"quantity"].abs(); df.loc[j,"profit"]=-df.loc[j,"profit"].abs()
# wrong totals
j=pick(.01); df.loc[j,"sales"]=(df.loc[j,"sales"]*rng.uniform(.8,1.2,len(j))).round(2)
# outlier amounts (bulk corporate orders - legitimate but extreme)
j=rng.choice(df.index[df.unit_price<3000],int(n*.0015),replace=False); df.loc[j,"quantity"]=rng.integers(40,90,len(j))
df.loc[j,"sales"]=(df.loc[j,"quantity"]*df.loc[j,"unit_price"]*(1-df.loc[j,"discount"])).round(2); df.loc[j,"profit"]=(df.loc[j,"sales"]*.12).round(2)
# exact duplicates
dups=df.sample(frac=.018,random_state=7)
df=pd.concat([df,dups],ignore_index=True).sample(frac=1,random_state=3).reset_index(drop=True)
df.insert(0,"row_id",range(1,len(df)+1))
df.drop(columns=["row_id"]).to_csv(OUT,index=False)
print("wrote",OUT,df.shape)

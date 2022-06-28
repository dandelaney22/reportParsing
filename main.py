import pandas as pd
import numpy as np
import os as os

os.getcwd()
path = r"C:\Users\dande\Desktop\Host"
os.chdir(path)
host = pd.read_csv("Host1.csv")

table = host[5:]
mapping = {table.columns[0]: 'col'}
table_ = table.rename(columns=mapping)
string_1 = table_['col'].astype('str')
string_1.dropna()
sub = 'Account'
x = string_1.str.find(sub)
table_['col1'] = x
table_['col1'] == 0
y = table_[table_['col1'] == 0]


z = table_[pd.to_numeric(table_['col'], errors='coerce').notnull()]
frames = [y,z]
yz = pd.concat(frames)
headers = yz.iloc[0]
df = pd.DataFrame(yz.values[1:], columns=headers)
df = df.rename(columns={"Environmental - Market": "Environmental"})

sub_cols = df[['Energy Plus Losses', 'Capacity', 'Environmental', 'MTC', 'Non Mass Market CC Adder', 'DRV', 'LSRV']]
sub_cols['Capacity'] = sub_cols['Capacity'].str.replace('$','')
sub_cols['Environmental'] = sub_cols['Environmental'].str.replace('$', '')
sub_cols['Energy Plus Losses'] = sub_cols['Energy Plus Losses'].str.replace('$', '')
sub_cols['DRV'] = sub_cols['DRV'].str.replace('$', '')
sub_cols['LSRV'] = sub_cols['LSRV'].str.replace('$', '')
sub_cols['DRV'] = pd.to_numeric(sub_cols['DRV'], errors='coerce')
sub_cols['Capacity'] = pd.to_numeric(sub_cols['Capacity'], errors='coerce')
sub_cols['Energy Plus Losses'] = pd.to_numeric(sub_cols['Energy Plus Losses'], errors='coerce')
sub_cols['LSRV'] = pd.to_numeric(sub_cols['LSRV'], errors = 'coerce')
sub_cols['Environmental'] = pd.to_numeric(sub_cols['Environmental'], errors = 'coerce')
sub_cols['MTC'] = pd.to_numeric(sub_cols['MTC'], errors = 'coerce')
sub_cols['Non Mass Market CC Adder'] = pd.to_numeric(sub_cols['Non Mass Market CC Adder'], errors = 'coerce')

sum1 = sub_cols.sum(axis=1)
TC = df['Total Credit']
ErrorFrame = TC.to_frame()
ErrorFrame['sum'] = sum1

ErrorFrame['Total Credit'] = ErrorFrame['Total Credit'].str.replace('$','')
ErrorFrame['Total Credit'] = pd.to_numeric(ErrorFrame['Total Credit'], errors='coerce')
Error = ErrorFrame['Total Credit'] - ErrorFrame['sum']
MOE = Error.between(-.01,0.01)
ErrorFrame['MOE'] = MOE


# Data Check #1: Do sub cols sum to equal Total Credit?

Error_Count = ErrorFrame['MOE'].count()
DataCheck1 = Error_Count > 0

# Data Check #2
# Does Total Net Gen =  Distribution Percentage * kWh Allocation?

gen_data = df[['Distribution Percentage','KWH Allocation']] ##Isolate relevant data
gen_data['Distribution Percentage'] = gen_data['Distribution Percentage'].str.replace('%','') ##remove %
gen_data['KWH Allocation'] =gen_data['KWH Allocation'].str.replace('%','')
gen_data[pd.to_numeric(gen_data['Distribution Percentage'], errors='coerce').notnull()]  #Convert to float64
gen_data['Distribution Percentage'] = pd.to_numeric(gen_data['Distribution Percentage'],errors = 'coerce')
gen_data['KWH Allocation'] = pd.to_numeric(gen_data['KWH Allocation'],errors = 'coerce')
gen_data['product'] = gen_data['Distribution Percentage'] * gen_data['KWH Allocation'] ## New column representing product of Distrib & KWH
prod = gen_data['product'].sum() ##sum of product column

mapping = {host.columns[0]: 'col0', host.columns[1]: 'TNG'} ##rename and isolate relevant columns
box = host.rename(columns=mapping)
box1 = box[['col0','TNG']]
mask = np.column_stack([box1[col0].astype(str).str.contains("Total Net Generation", na=False) for col0 in box1])
ErrorFrame1 = box.loc[mask.any(axis=1)]
ErrorFrame1['product'] = prod

TNG = ErrorFrame1['TNG'].str.replace(',', '').astype(float)
margin = TNG/prod
DataCheck2 = margin.between(-.01,0.01)

#Data Check 3
mask1 = np.column_stack([df[col].astype(str).str.contains("No MTC", na=False) for col in df])
No_MTC = df.loc[mask1.any(axis=1)]
No_MTC['Distribution Percentage'] = No_MTC['Distribution Percentage'].str.replace('%', '')
sum2 = No_MTC['Distribution Percentage'].astype(float)
DataCheck3 = (sum2.sum()) >.4

#Data Check 4
Total_Credit = df['Total Credit'].count()
Energy_Plus_Losses= sub_cols['Energy Plus Losses'].count()
Capacity = sub_cols['Capacity'].count()
Env_Mkt = sub_cols['Environmental'].count()
MTC = sub_cols['MTC'].count()
CC_Adder = sub_cols['Non Mass Market CC Adder'].count()
DRV = sub_cols['DRV'].count()
LSRV = sub_cols['LSRV'].count()

MV_EPL = Total_Credit - Energy_Plus_Losses
MV_Cap = Total_Credit - Capacity
MV_Env_Mkt = Total_Credit - Env_Mkt
MV_MTC = Total_Credit - MTC
MV_CC_Adder = Total_Credit - CC_Adder
MV_DRV = Total_Credit - DRV
MV_LSRV = Total_Credit - LSRV

MV = {'Energy_Plus_Losses': [MV_EPL], 'Capacity': [MV_Cap], 'Env_Mkt': [MV_Env_Mkt], 'MTC': [MV_MTC],'CC_Adder': [MV_CC_Adder], 'DRV': [MV_DRV],'LSRV': [MV_LSRV]}
Missing = pd.DataFrame.from_dict(MV)
DataCheck4 = Missing !=0


#Data Check 5
dist = df['Distribution Percentage'].str.replace('%','')
df5 = dist.to_frame()
df5.iloc[1: , :]
df5 = pd.to_numeric(df5['Distribution Percentage'],errors = 'coerce')
df5.dropna()
DataCheck5 = df5.sum() == 1.0

#Data Check 6
DataCheck6 = df["Account Number"].is_unique
# True Indicates No Duplicate Account Numbers

from collections import namedtuple
import altair as alt
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import streamlit as st
import requests
import numpy as np
import datetime

sym = "LINKUSDT"

url = f'https://fapi.binance.com/fapi/v1/trades?symbol={sym}&limit=1000'

# extract tape data and analyse the data 
trans_all = pd.DataFrame()
for i in range(0,1):
    transaction = requests.get(url).json()
    trans_df = pd.DataFrame(transaction,index=None)
    trans_df['quoteQty']=trans_df['quoteQty'].astype(float)
    trans_df['price']=trans_df['price'].astype(float)
    trans_df['time']=trans_df['time'].astype(int)
    trans_df = trans_df.sort_values('time', ascending=True).reset_index(drop=True)
    trans_df['time']=trans_df['time'].apply(lambda d: datetime.datetime.fromtimestamp(int(d)/1000).strftime('%Y-%m-%d %H:%M:%S'))
    trans_all = pd.concat([trans_all, trans_df], ignore_index=True)
    #time.sleep(50)
    
trans_all = trans_all.drop_duplicates()
trans_all = trans_all.sort_values('time', ascending=True).reset_index(drop=True)
cal_trans_df = trans_all[['price','time','isBuyerMaker','quoteQty']]
grouped_df = cal_trans_df.groupby(['price', 'time','isBuyerMaker']).agg({'quoteQty': ['sum', 'size']})
grouped_df = grouped_df.reset_index()
grouped_df.columns = [' '.join(col).strip() for col in grouped_df.columns.values]
grouped_df.loc[(grouped_df['isBuyerMaker']==True), 'filled_by'] = 'Seller'
grouped_df.loc[(grouped_df['isBuyerMaker']==False), 'filled_by'] = 'Buyer'
grouped_df = grouped_df.sort_values('time', ascending=True).reset_index(drop=True)
print(grouped_df)

seller_tape = grouped_df[grouped_df['filled_by'] == 'Seller']
s_avg_p = (seller_tape['price'] * seller_tape['quoteQty sum']).sum()/seller_tape['quoteQty sum'].sum()
s_num_t = seller_tape['quoteQty size'].sum()
seller_tape = seller_tape[['time','quoteQty sum','quoteQty size']]
seller_tape = seller_tape.rename(columns={'quoteQty sum':'seller_quoteQty','quoteQty size':'seller_num'})

buyer_tape = grouped_df[grouped_df['filled_by'] == 'Buyer']
b_avg_p = (buyer_tape['price'] * buyer_tape['quoteQty sum']).sum()/buyer_tape['quoteQty sum'].sum()
b_num_t = buyer_tape['quoteQty size'].sum()
buyer_tape = buyer_tape[['time','quoteQty sum','quoteQty size']]
buyer_tape = buyer_tape.rename(columns={'quoteQty sum':'buyer_quoteQty','quoteQty size':'buyer_num'})

seller_quoteQty = seller_tape['seller_quoteQty'].sum()
print("Seller quoteQty:", seller_quoteQty, s_avg_p, s_num_t)
buyer_quoteQty = buyer_tape['buyer_quoteQty'].sum()
print("Buyer quoteQty:", buyer_quoteQty, b_avg_p, b_num_t)

price_tape = grouped_df[['time','price']]
price_tape = price_tape.drop_duplicates(subset='time', keep='first').reset_index(drop=True)
time0 = price_tape['time'][0]
time1 = price_tape['time'].iloc[-1]
print("time:", time0, time1)

merged_df = pd.merge(price_tape, seller_tape, on='time', how='left')
merged_df = pd.merge(merged_df, buyer_tape, on='time', how='left')
merged_df = merged_df.sort_values('time', ascending=True).reset_index(drop=True)
time = merged_df['time']
merged_df['buyer_quoteQty'] = merged_df['buyer_quoteQty'].fillna(0)
merged_df['seller_quoteQty'] = merged_df['seller_quoteQty'].fillna(0)
merged_df['diff_buyer_seller'] = merged_df['buyer_quoteQty'] - merged_df['seller_quoteQty']
seller_quoteQty = merged_df['seller_quoteQty']
buyer_quoteQty = merged_df['buyer_quoteQty']
price = merged_df['price']
diff_buyer_seller = merged_df['diff_buyer_seller'] 

############first chart for tape (trend and movement of buyer and seller)
# Create bar trace for diff_buyer_seller
colors = ['red' if value < 0 else 'blue' for value in diff_buyer_seller]
bar_trace = go.Bar(x=time, y=diff_buyer_seller, name='diff_buyer_seller', marker=dict(color=colors), opacity=0.5)

# Create line trace for price
line_trace = go.Scatter(x=time, y=price, name='price', yaxis='y2', line=dict(color='green'))

# Create layout for the axes and title
layout = go.Layout(
    title='Quantity and Price over Time',
    xaxis=dict(title='Time'),
    yaxis=dict(title='Quantity'),
    yaxis2=dict(title='Price', overlaying='y', side='right'),
    shapes=[
        # Add a horizontal line at y=0 on the first y-axis
        dict(type='line', yref='y', y0=0, y1=0, xref='x', x0=min(time), x1=max(time), line=dict(color='grey', dash='dot'))
    ]
)

# Create the figure and add the traces
fig = go.Figure(data=[bar_trace, line_trace], layout=layout)

# Show the figure
st.plotly_chart(fig)

############second chart for 4 subplot
from plotly.subplots import make_subplots

# Create traces for each bar chart
buyer_quoteQty_trace = go.Bar(x=time, y=merged_df['buyer_quoteQty'], name='Buyer Quote Quantity', marker=dict(color='green'), opacity=0.5)
buyer_num_trace = go.Bar(x=time, y=merged_df['buyer_num'], name='Buyer Number', marker=dict(color='green'), opacity=0.5)
seller_quoteQty_trace = go.Bar(x=time, y=merged_df['seller_quoteQty'], name='Seller Quote Quantity', marker=dict(color='purple'), opacity=0.5)
seller_num_trace = go.Bar(x=time, y=merged_df['seller_num'], name='Seller Number', marker=dict(color='purple'), opacity=0.5)

# Create subplot figure
fig = make_subplots(rows=2, cols=2, subplot_titles=('Buyer Quote Quantity', 'Buyer Number', 'Seller Quote Quantity', 'Seller Number'))

# Add each trace to the appropriate subplot
fig.add_trace(buyer_quoteQty_trace, row=1, col=1)
fig.add_trace(buyer_num_trace, row=1, col=2)
fig.add_trace(seller_quoteQty_trace, row=2, col=1)
fig.add_trace(seller_num_trace, row=2, col=2)

# Update yaxis properties
qty_min = merged_df['buyer_quoteQty'].min()
qty_max = merged_df['buyer_quoteQty'].max()
num_min = merged_df['buyer_num'].min()
num_max = merged_df['buyer_num'].max()
fig.update_yaxes(range=[qty_min, qty_max], row=1, col=1)
fig.update_yaxes(range=[num_min, num_max], row=1, col=2)
fig.update_yaxes(range=[qty_min, qty_max], row=2, col=1)
fig.update_yaxes(range=[num_min, num_max], row=2, col=2)

# Update layout for the axes and title
fig.update_layout(
    xaxis=dict(title='Time'),
    yaxis=dict(title='Quantity'),
)

# Show the figure
st.plotly_chart(fig)

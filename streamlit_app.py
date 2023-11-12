from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import streamlit as st

from binance.um_futures import UMFutures
import pandas as pd
import numpy as np
import datetime
import math
import time
import matplotlib.pyplot as plt

um_futures_client = UMFutures()
sym = "LINKUSDT"


############first chart for tape (trend and movement of buyer and seller)
# Create bar trace for diff_buyer_seller
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
fig.show()


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
fig.show()

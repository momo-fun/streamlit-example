from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import streamlit as st

# Create some example data
x_data = ['A', 'B', 'C', 'D', 'E']
y1_data = [1, 2, 3, 2, 1]
y2_data = [2, 1, 2, 3, 4]

# Create a bar trace
bar_trace = go.Bar(x=x_data, y=y1_data, name='Bar data')

# Create a line trace
line_trace = go.Scatter(x=x_data, y=y2_data, name='Line data', yaxis='y2')

# Create a layout with a secondary y-axis
layout = go.Layout(
    yaxis=dict(title='Bar data'),
    yaxis2=dict(title='Line data', overlaying='y', side='right'),
)

# Create a figure and add the traces
fig = go.Figure(data=[bar_trace, line_trace], layout=layout)

# Display the figure in Streamlit
st.plotly_chart(fig)

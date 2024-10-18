import streamlit as st
import pandas as pd
import altair as alt
from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import QueryBase
import time

st.set_page_config(page_title="eUSD Price Peg", page_icon="📊")

# Retrieve Dune API key from Streamlit secrets
try:
    dune_api_key = st.secrets["DUNE_API_KEY"]
except KeyError:
    st.error("Dune API Key not found. Please set the DUNE_API_KEY secret.")
    
    st.stop()

# Function to fetch data from Dune Analytics
@st.cache_data(ttl=3600)
def fetch_dune_data(query_id, timeperiod):
    dune = DuneClient(dune_api_key)
    query = QueryBase(
        query_id=query_id,
        params=[QueryParameter.text_type(name="timeperiod", value=timeperiod)]
    )
    results = dune.run_query_dataframe(query)
    return results

st.title("eUSD Price Peg")

# Sidebar for user input
query_id = 3950965  # Your specific query ID
timeperiod = "day"

# Define the color scheme
network_colors = {
    'Ethereum': '#bf8700',
    'Base': '#0078bf',
    'Arbitrum': '#00af50'
}

# Define legend data
legend_data = [
    {"range": (0.999, 1.001), "color": "rgba(0, 255, 0, 0.1)", "description": "Excellent"},
    {"range": (0.998, 1.002), "color": "rgba(255, 255, 0, 0.1)", "description": "Good"},
    {"range": (0.995, 1.005), "color": "rgba(255, 165, 0, 0.1)", "description": "Fair"},
    {"range": (0.990, 1.010), "color": "rgba(255, 0, 0, 0.1)", "description": "Poor"}
]

# Highlight function
def highlight_outliers(val):
    if pd.isna(val):
        return ''
    for item in legend_data:
        if item["range"][0] <= val <= item["range"][1]:
            return f'background-color: {item["color"]}'
    return ''

# Function to display the main content
def display_content(df):
    df['hour'] = pd.to_datetime(df['hour'])
    df_long = df.melt(
        id_vars='hour', 
        value_vars=['avg_price_ethereum', 'avg_price_base', 'avg_price_arbitrum'],
        var_name='network', 
        value_name='avg_price'
    )
    df_long['network'] = df_long['network'].replace({
        'avg_price_ethereum': 'Ethereum',
        'avg_price_base': 'Base',
        'avg_price_arbitrum': 'Arbitrum'
    })
    df_long['avg_price'] = pd.to_numeric(df_long['avg_price'], errors='coerce')

    # Create Altair chart with selection
    selection = alt.selection_point(fields=['network'], bind='legend')
    
    chart = alt.Chart(df_long).mark_line().encode(
        x='hour:T',
        y=alt.Y('avg_price:Q', scale=alt.Scale(domain=[0.985, 1.015]), title='Average Price'),
        color=alt.Color('network:N', scale=alt.Scale(domain=list(network_colors.keys()), range=list(network_colors.values()))),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        selection
    ).properties(
        width=800,
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # Monthly average table
    try:
        monthly_avg_df = df_long.set_index('hour').groupby('network').resample('M')['avg_price'].mean().unstack(level=0)
        monthly_avg_df.index = monthly_avg_df.index.strftime('%B')

        average_row = monthly_avg_df.mean().to_frame().T
        average_row.index = ['Average']
        monthly_avg_df_with_avg = pd.concat([monthly_avg_df, average_row])

        st.subheader("Monthly Averages")
        st.dataframe(monthly_avg_df_with_avg.style.applymap(highlight_outliers), use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while calculating monthly averages: {str(e)}")

# Main execution
if 'data' not in st.session_state:
    with st.spinner("Loading initial data... This may take up to 30 seconds."):
        try:
            df = fetch_dune_data(query_id, timeperiod)
            st.session_state.data = df
        except Exception as e:
            st.error(f"An error occurred while fetching initial data: {str(e)}")

if 'data' in st.session_state:
    display_content(st.session_state.data)

st.sidebar.subheader("Legend")

# Network color legend
st.sidebar.subheader("Network Colors")
for network, color in network_colors.items():
    st.sidebar.markdown(
        f'<div style="display: flex; align-items: center;">'
        f'<div style="width: 20px; height: 20px; background-color: {color}; margin-right: 10px;"></div>'
        f'<div>{network}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
st.sidebar.markdown('---')
# Custom legend
st.sidebar.subheader("Price Range")
for item in legend_data:
    st.sidebar.markdown(
        f'<div style="display: flex; align-items: center;">'
        f'<div style="width: 20px; height: 20px; background-color: {item["color"]}; margin-right: 10px;"></div>'
        f'<div>{item["range"][0]} - {item["range"][1]}: {item["description"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
st.sidebar.markdown('---')

# Footer
st.markdown("---")
st.markdown("Data provided by Dune Analytics")
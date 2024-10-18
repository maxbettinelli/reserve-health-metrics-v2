import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Base Analysis", layout="wide")

# Get current date
current_date = datetime.now().strftime("%B %d %Y")

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('base_memecoins_reduced.csv', index_col='name')
    for col in ['24h_change', '7d_change', '30d_change']:
        df[col] = df[col].str.rstrip('%').astype('float') / 100.0
    df['price'] = df['price'].str.lstrip('$').astype('float')
    df['market_cap'] = df['market_cap'].str.lstrip('$').str.replace(',', '').astype('float')
    df = df[df['market_cap'] > 1000000] # change to get market caps above X amount 
    return df

df = load_data()

st.title(f"Base")

# Custom color scale with darker red and green
color_scale = [
    [0, 'rgb(139, 0, 0)'],     # Dark red
    [0.25, 'rgb(255, 99, 71)'],  # Tomato
    [0.5, 'rgb(220, 220, 220)'], # Dark for the midpoint
    [0.75, 'rgb(144, 238, 144)'],# Light green
    [1, 'rgb(0, 100, 0)']      # Dark green
]

# Function to create treemap
def create_treemap(df):
    try:
        fig = px.treemap(
            df,
            path=[px.Constant("All"), df.index],
            values='market_cap',
            color='24h_change',# Line 44 and 67 should correspond with each other
            hover_data=['symbol', 'price', 'market_cap', '24h_change', '7d_change', '30d_change'],
            color_continuous_scale=color_scale,
            color_continuous_midpoint=0
        )

        # Update text and hover info
        fig.update_traces(
            textposition="middle center",
            texttemplate="<b>%{label}</b>",
            hovertemplate='<b>%{label}</b><br>' +
                          'Market Cap: $%{customdata[2]:,.0f}<br>' +
                          '24h Change: %{customdata[3]:.2%}<br>' +
                          'Weekly Change: %{customdata[4]:.2%}<br>' +
                          'Monthly Change: %{customdata[5]:.2%}<br>'
        )

        fig.update_layout(
            title_text=f'Base Memecoins by Market Cap - {current_date}',
            title_x=0,
            width=1000,
            height=600,
            coloraxis_colorbar=dict(
                title="Daily Change", # Line 44 and 67 should correspond with each other
                tickformat=".0%"
            )
        )

        return fig
    except Exception as e:
        st.error(f"An error occurred while creating the treemap: {str(e)}")
        return None

# Create and display the treemap
fig_treemap = create_treemap(df)
if fig_treemap:
    st.plotly_chart(fig_treemap, use_container_width=True)
else:
    st.warning("Unable to create treemap. Please check your data.")

# Create pie chart for market cap distribution
def create_pie_chart(df):
    df_sorted = df.sort_values('market_cap', ascending=False)
    total_market_cap = df_sorted['market_cap'].sum()
    df_sorted['market_cap_percentage'] = df_sorted['market_cap'] / total_market_cap * 100
    top_10 = df_sorted.head(10)
    others = pd.DataFrame({
        'market_cap': df_sorted.iloc[10:]['market_cap'].sum(),
        'market_cap_percentage': df_sorted.iloc[10:]['market_cap_percentage'].sum()
    }, index=['Others'])
    df_pie = pd.concat([top_10, others])

    fig = go.Figure(data=[go.Pie(
        labels=df_pie.index,
        values=df_pie['market_cap_percentage'],
        hole=.3,
        hovertemplate="<b>%{label}</b><br>Market Cap: $%{customdata:,.0f}<br>Percentage: %{percent}<extra></extra>",
        customdata=df_pie['market_cap']
    )])

    fig.update_layout(
        title_text=f'Market Cap Distribution (Top 10 + Others)',
        title_x=0.5,
        width=800,
        height=500
    )

    return fig

# Create and display the pie chart
fig_pie = create_pie_chart(df)
st.plotly_chart(fig_pie, use_container_width=True)

# Display the dataframe
if st.checkbox('Detailed Base Data', value=True):
    st.dataframe(df)

    # Display data statistics
    st.subheader(f"Data Statistics - {current_date}")
    st.write(f"Total market cap: ${df['market_cap'].sum():,.2f}")
    st.write(f"Number of coins with $100k+ market cap: {(df['market_cap'] > 100000).sum()}")
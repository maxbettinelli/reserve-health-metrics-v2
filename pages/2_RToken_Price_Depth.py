import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="RToken Liquidity Analysis", layout="wide")

# Function to load data
@st.cache_data
def load_data():
    filename = "rtoken_liquidity.csv"
    df = pd.read_csv(filename)
    return df

# Load the data
df = load_data()

# Create the line plot
st.title("RToken Price Depth")

# Get date columns dynamically
date_columns = [col for col in df.columns if col not in ['Asset Name', 'Weekly Change']]

# Melt the DataFrame for plotting
df_melted = df.melt(id_vars=['Asset Name', 'Weekly Change'], 
                    value_vars=date_columns,
                    var_name='Week', 
                    value_name='Value')

# Convert Value column to numeric, removing $ and commas
df_melted['Value'] = df_melted['Value'].replace('[\$,]', '', regex=True).astype(float)

# Convert Week to datetime
df_melted['Week'] = pd.to_datetime(df_melted['Week'], format='%m/%d')

# Sort the DataFrame by Week
df_melted = df_melted.sort_values('Week')

# Create the plot
fig = px.line(df_melted, x='Week', y='Value', color='Asset Name', 
              title='RToken Liquidity Over Time',
              labels={'Value': 'Liquidity ($)', 'Week': 'Date'},
              hover_data=['Asset Name', 'Value'])

fig.update_layout(
    legend_title_text='Asset Name',
    xaxis_title='Date',
    yaxis_title='Liquidity ($)',
    xaxis=dict(
        tickmode='auto',
        nticks=10,
        tickformat='%m/%d'
    )
)

st.plotly_chart(fig, use_container_width=True)

# Display the data table with conditional formatting
st.subheader("RToken Liquidity Data")

# Function to color cells based on positive/negative values
def color_negative_red(val):
    if isinstance(val, str) and val.endswith('%'):
        value = float(val.rstrip('%'))
        color = 'green' if value >= 0 else 'red'
        return f'color: {color}'
    return ''

# Apply the styling
styled_df = df.style.applymap(color_negative_red, subset=['Weekly Change'])

# Display the styled DataFrame
st.dataframe(styled_df, use_container_width=True)

if st.checkbox('See Graph'):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image('Liquidity_comparison_9.26.24.png', caption='26 September 2024')
    with col2:
        st.image('Liquidity_comparison_10.4.24.png', caption='4 October 2024')
    with col3:
        st.image('Liquidity_comparison_10.9.24.png', caption='9 October 2024')

# Add some explanatory text
st.markdown("""
- The chart measures the amount of an RToken you can swap on a DEX Aggregator (Odos) in a single transaction before incurring a 0.5% price impact. 
""")
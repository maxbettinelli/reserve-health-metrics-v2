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

# Melt the DataFrame for plotting
df_melted = df.melt(id_vars=['Asset Name', 'Weekly Change'], 
                    value_vars=['8/1', '8/8', '8/15', '8/22', '8/29', '9/4', '9/13'],
                    var_name='Week', 
                    value_name='Value')

# Convert Value column to numeric, removing $ and commas
df_melted['Value'] = df_melted['Value'].replace('[\$,]', '', regex=True).astype(float)

# Create a custom order for the weeks
week_order = ['8/1', '8/8', '8/15', '8/22', '8/29', '9/4', '9/13']
df_melted['Week'] = pd.Categorical(df_melted['Week'], categories=week_order, ordered=True)

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
        tickmode='array',
        tickvals=week_order,
        ticktext=week_order
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
    st.image('Liquidity_comparison_9.4.24.png')
    st.image('Liquidity_comparison_9.13.24.png')
# Add some explanatory text
st.markdown("""
- The chart measures the amount of an RToken you can swap on a DEX Aggregator (Odos) in a single transaction before incurring a 0.5% price impact. 
""")
import streamlit as st
import pandas as pd
import altair as alt
from dune_client.client import DuneClient

st.set_page_config(page_title="FinTech AUM", page_icon="📊", layout="wide")

# Retrieve Dune API key from Streamlit secrets
dune_api_key = st.secrets["DUNE_API_KEY"]

# Function to fetch data from Dune Analytics
@st.cache_data(ttl=3600)
def fetch_dune_data(query_id):
    dune = DuneClient(dune_api_key)
    results = dune.get_latest_result_dataframe(query_id)
    return results

# Function to safely convert to numeric
def safe_numeric(val):
    try:
        return pd.to_numeric(val)
    except ValueError:
        return 0

# Function to format currency
def format_currency(value):
    return f"${value:,.2f}"

st.title("FinTech AUM")

# Fetch data
query_id = 4019395
df = fetch_dune_data(query_id)

# Data preprocessing
df['date'] = pd.to_datetime(df['date'])
for col in ['ugly_cash_base_balance', 'ugly_cash_eth_balance', 'sentz_base_balance', 'sentz_eth_balance']:
    df[col] = df[col].apply(safe_numeric)

df['ugly_cash_total'] = df['ugly_cash_base_balance'] + df['ugly_cash_eth_balance']
df['sentz_total'] = df['sentz_base_balance'] + df['sentz_eth_balance']
df['total_aum'] = df['ugly_cash_total'] + df['sentz_total']

# Sort dataframe with most recent date at the top
df = df.sort_values('date', ascending=False)

# Add company selection in sidebar
st.sidebar.title("Settings")
selected_company = st.sidebar.radio("Select FinTech Company", ["All", "Ugly Cash", "Sentz"])

# Filter data based on selection
if selected_company == "Ugly Cash":
    chart_data = df[['date', 'ugly_cash_total']].rename(columns={'ugly_cash_total': 'balance'})
    chart_data['company'] = 'Ugly Cash'
elif selected_company == "Sentz":
    chart_data = df[['date', 'sentz_total']].rename(columns={'sentz_total': 'balance'})
    chart_data['company'] = 'Sentz'
else:
    chart_data = df.melt(id_vars=['date'], value_vars=['ugly_cash_total', 'sentz_total'], 
                         var_name='company', value_name='balance')
    chart_data['company'] = chart_data['company'].map({'ugly_cash_total': 'Ugly Cash', 'sentz_total': 'Sentz'})

# Create stacked area chart
chart = alt.Chart(chart_data).mark_area().encode(
    x='date:T',
    y=alt.Y('balance:Q', stack='zero'),
    color=alt.Color('company:N', scale=alt.Scale(domain=['Ugly Cash', 'Sentz'],
                                                 range=['#bf8700', '#0078bf'])),
    tooltip=['date', 'company', 'balance']
).properties(
    width=800,
    height=400
).interactive()

# Display the chart
st.altair_chart(chart, use_container_width=True)

# Calculate monthly changes
latest_date = df['date'].max()
month_ago_date = latest_date - pd.Timedelta(days=30)

latest_data = df.iloc[0]
month_ago_data = df[df['date'] <= month_ago_date].iloc[0]

# Display current balances and monthly changes
col1, col2, col3 = st.columns(3)

def display_company_stats(column, company, current, month_ago):
    with column:
        st.markdown(f"### {company} Balance:")
        st.markdown(f"## {format_currency(current)} eUSD")
        monthly_change = current - month_ago
        change_color = "green" if monthly_change >= 0 else "red"
        st.markdown(f'<span style="color:{change_color};">Monthly Change (30 days): {format_currency(monthly_change)} eUSD</span>', unsafe_allow_html=True)

if selected_company in ["All", "Ugly Cash"]:
    display_company_stats(col1, "Ugly Cash", latest_data['ugly_cash_total'], month_ago_data['ugly_cash_total'])

if selected_company in ["All", "Sentz"]:
    display_company_stats(col2, "Sentz", latest_data['sentz_total'], month_ago_data['sentz_total'])

# Display total AUM
current_total_aum = latest_data['total_aum'] if selected_company == "All" else (
    latest_data['ugly_cash_total'] if selected_company == "Ugly Cash" else latest_data['sentz_total']
)
month_ago_total_aum = month_ago_data['total_aum'] if selected_company == "All" else (
    month_ago_data['ugly_cash_total'] if selected_company == "Ugly Cash" else month_ago_data['sentz_total']
)
display_company_stats(col3, "Total AUM", current_total_aum, month_ago_total_aum)

# Option to view raw data
if st.checkbox('View detailed FinTech Data', value=False):
    st.dataframe(df)
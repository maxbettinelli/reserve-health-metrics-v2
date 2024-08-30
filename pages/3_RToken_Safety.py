import pandas as pd
import streamlit as st

todays_date = 'Data: August 29th'
last_weeks_date = 'Data: August 22nd'
df = pd.read_csv('rtoken_safety.csv')

# Define a function to highlight values under 1 with red, with alpha of .1
def highlight_values(val):
    if val < 1:
        return 'background-color: rgba(255, 0, 0, 0.1)'  # Red with alpha of .1
    return ''

# Apply the highlighting to the DataFrame
styled_df = df.style.applymap(highlight_values, subset=["8/29", "8/22", "8/16"])

# Streamlit app
st.set_page_config(layout="wide")

st.markdown("# RToken Safety")
st.markdown("---")

st.sidebar.markdown("# RToken Safety")
st.sidebar.markdown("---")

# Create two columns with a 2:1 ratio
col1, col2 = st.columns([2, 1])

# Display the styled DataFrame in the left column
with col1:
    st.markdown('What portion of an RToken can we redeem?')
    st.dataframe(styled_df, use_container_width=True)

# Display the explanation in the right column
with col2:
    st.markdown('''
                **Legend:**
                
                ---
                ''')
    st.markdown("""
    
    - **0 - 1**: Bad
    - **1+**: Good
    - **2+**: Great
    - Higher: 🚀 
    """)

if st.checkbox('Formula Details'):
    # Display the formula using LaTeX in Streamlit
    st.latex(r'''
    \text{Score} = \min \left( \frac{\text{Idle\_Lending\_Market\_Liquidity}_1}{\text{Collateral\_in\_RToken}_1}, \frac{\text{Available\_DEX\_Liquidity}_2}{\text{Collateral\_in\_RToken}_2}, \dots, \frac{\text{Available\_Liquidity}_n}{\text{Collateral\_in\_RToken}_n} \right)
    ''')

st.markdown("---")

if st.checkbox('View Collateral Liquidity Charts', value=True):
    st.subheader('Collateral Liquidity on DEXs')
    col1, col2 = st.columns(2)
    with col1:
        st.image("collateral_8.29.png", caption=todays_date, use_column_width=True)
    with col2:
        st.image("collateral_8.22.png", caption=last_weeks_date, use_column_width=True)
if st.checkbox('View ETH+ Redemption Liquidity', value=False):

    st.subheader('ETH+ Redemption Liquidity')
    col1, col2 = st.columns(2)
    with col1:
        st.image("currentbasket_8.29.png", caption=todays_date, use_column_width=True)
    with col2:
        st.image("currentbasket_8.22.png", caption=last_weeks_date, use_column_width=True)

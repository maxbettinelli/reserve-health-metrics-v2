import streamlit as st

# Set page config
st.set_page_config(page_title="Health Metrics Dashboard", layout="wide")

# Custom CSS for minimal styling
st.markdown("""
    <style>
    .stImage > img {
        width: 150px !important;
        margin-bottom: 10px;
    }
    .button-link {
        display: inline-block;
        padding: 0.5em 1em;
        margin: 0.5em 0;
        text-decoration: none;
        color: #0151af;
        background-color: rgba(1, 81, 175, 0.1);
        border-radius: 4px;
        text-align: left;
        width: 100%;
    }
    .button-link:hover {
        background-color: rgba(1, 81, 175, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Header with logo and title

st.image('reserve-blue.png', width=250)
st.markdown("---")
st.subheader("Health Metrics Dashboard")
st.markdown("---")

# Define a function to create a blue button-like link
def blue_button_link(text, url):
    return f'<a href="{url}" target="_blank" class="button-link">{text}</a>'

# Sections with links
sections = {
    "Reserve": [
        ("Register", "https://app.reserve.org/"),
        ("ETH+", "https://app.reserve.org/ethereum/token/0xe72b141df173b999ae7c1adcbf60cc9833ce56a8/overview"),
        ("eUSD", "https://app.reserve.org/ethereum/token/0xa0d69e286b938e21cbf7e51d71f6a4c8918f482f/overview")
    ],
    "Lending": [
        ("Morpho Borrow", "https://app.morpho.org/borrow?network=mainnet&morphoPrice=0.65"),
        ("Morpho Earn", "https://app.morpho.org/?network=mainnet&morphoPrice=0.65"),
        ("Ionic", "https://app.ionic.money/market?chain=8453&pool=0")
    ],
    "DEXs": [
        ("Curve", "https://curve.fi/#/ethereum/pools"),
        ("Uniswap", "https://app.uniswap.org/pool"),
        ("Aerodrome", "https://aerodrome.finance/liquidity")
    ]
}

for section, links in sections.items():
    st.subheader(section)
    for text, url in links:
        st.markdown(blue_button_link(text, url), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("© 2024 Reserve Protocol.")
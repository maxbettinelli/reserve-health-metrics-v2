import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objs as go
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Use caching for data fetching and processing functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_liquidation_data():
    query = gql("""
    query {
      transactions(
        where: {
          marketUniqueKey_in: [
            "0x3f4d007982a480dd99052c05d811cf6838ce61b2a2be8dc52fca107f783d1f15"
            "0x461da96754b33fec844fc5e5718bf24298a2c832d8216c5ffd17a5230548f01f"
            "0x6029eea874791e01e2f3ce361f2e08839cd18b1e26eea6243fa3e43fe8f6fa23"
            "0xf9ed1dba3b6ba1ede10e2115a9554e9c52091c9f1b1af21f9e0fecc855ee74bf"
            "0x3a5bdf0be8d820c1303654b078b14f8fc6d715efaeca56cec150b934bdcbff31"
            "0xb5d424e4af49244b074790f1f2dc9c20df948ce291fc6bcc6b59149ecf91196d"
            "0xce89aeb081d719cd35cb1aafb31239c4dfd9c017b2fec26fc2e9a443461e9aea"
          ]
          type_in: [MarketLiquidation]
        }
      ) {
        items {
          blockNumber
          hash
          type
          user {
            address
          }
          data {
            ... on MarketLiquidationTransactionData {
              seizedAssets
              repaidAssets
              seizedAssetsUsd
              repaidAssetsUsd
              badDebtAssetsUsd
              liquidator
              market {
                uniqueKey
              }
            }
          }
        }
      }
    }
    """)

    transport = RequestsHTTPTransport(
        url="https://blue-api.morpho.org/graphql",
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client.execute(query)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_market_data():
    query = gql("""
    query SpecificMarkets {
      markets(
        first: 100
        where: {
          uniqueKey_in: [
            "0x3f4d007982a480dd99052c05d811cf6838ce61b2a2be8dc52fca107f783d1f15"
            "0x461da96754b33fec844fc5e5718bf24298a2c832d8216c5ffd17a5230548f01f"
            "0x6029eea874791e01e2f3ce361f2e08839cd18b1e26eea6243fa3e43fe8f6fa23"
            "0xf9ed1dba3b6ba1ede10e2115a9554e9c52091c9f1b1af21f9e0fecc855ee74bf"
            "0x3a5bdf0be8d820c1303654b078b14f8fc6d715efaeca56cec150b934bdcbff31"
            "0xb5d424e4af49244b074790f1f2dc9c20df948ce291fc6bcc6b59149ecf91196d"
            "0xce89aeb081d719cd35cb1aafb31239c4dfd9c017b2fec26fc2e9a443461e9aea"
            "0x9ec52d7195bafeba7137fa4d707a0f674a04a6d658c9066bcdbebc6d81eb0011"
            "0xdf6aa0df4eb647966018f324db97aea09d2a7dde0d3c0a72115e8b20d58ea81f"
          ]
        }
      ) {
        items {
          id
          uniqueKey
          lltv
          oracleAddress
          irmAddress
          creationBlockNumber
          creationTimestamp
          creatorAddress
          whitelisted
          collateralPrice
          reallocatableLiquidityAssets
          targetBorrowUtilization
          targetWithdrawUtilization
          loanAsset {
            address
            symbol
            decimals
          }
          collateralAsset {
            address
            symbol
            decimals
          }
          oracle {
            address
            type
          }
          state {
            borrowAssets
            supplyAssets
            borrowAssetsUsd
            supplyAssetsUsd
            borrowShares
            supplyShares
            liquidityAssets
            liquidityAssetsUsd
            collateralAssets
            collateralAssetsUsd
            utilization
            rateAtUTarget
            supplyApy
            borrowApy
            netSupplyApy
            netBorrowApy
            fee
            timestamp
          }
          concentration {
            supplyHhi
            borrowHhi
          }
          badDebt {
            underlying
            usd
          }
          realizedBadDebt {
            underlying
            usd
          }
          dailyApys {
            supplyApy
            borrowApy
            netSupplyApy
            netBorrowApy
          }
          warnings {
            type
            level
          }
        }
      }
    }
    """)

    transport = RequestsHTTPTransport(
        url="https://blue-api.morpho.org/graphql",
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client.execute(query)

@st.cache_data
def process_liquidation_data(response):
    rename_dict = {
        '0x3f4d007982a480dd99052c05d811cf6838ce61b2a2be8dc52fca107f783d1f15': 'ETH+/eUSD',
        '0x461da96754b33fec844fc5e5718bf24298a2c832d8216c5ffd17a5230548f01f': 'WBTC/eUSD',
        '0x6029eea874791e01e2f3ce361f2e08839cd18b1e26eea6243fa3e43fe8f6fa23': 'wstETH/eUSD',
        '0x9ec52d7195bafeba7137fa4d707a0f674a04a6d658c9066bcdbebc6d81eb0011': 'ETH+/WETH',
        '0xf9ed1dba3b6ba1ede10e2115a9554e9c52091c9f1b1af21f9e0fecc855ee74bf': 'bsdETH/eUSD (Base)',
        '0x3a5bdf0be8d820c1303654b078b14f8fc6d715efaeca56cec150b934bdcbff31': 'hyUSD/eUSD (Base)',
        '0xb5d424e4af49244b074790f1f2dc9c20df948ce291fc6bcc6b59149ecf91196d': 'cbETH/eUSD (Base)',
        '0xce89aeb081d719cd35cb1aafb31239c4dfd9c017b2fec26fc2e9a443461e9aea': 'wstETH/eUSD (Base)'
    }

    items = response['transactions']['items']
    df = pd.json_normalize(items)
    df = df.sort_values(by='blockNumber', ascending=True)
    df['total_liquidations'] = df.groupby('data.market.uniqueKey')['data.seizedAssetsUsd'].cumsum()
    df['data.market.uniqueKey'] = df['data.market.uniqueKey'].map(rename_dict).fillna(df['data.market.uniqueKey'])
    df_selected = df[['blockNumber', 'type', 'user.address', 'data.market.uniqueKey', 'data.seizedAssetsUsd', 'hash', 'total_liquidations']]
    df_selected.columns = ['blockNumber', 'type', 'user', 'market', 'seizedAssetsUsd', 'hash', 'liquidations_total']
    return df_selected

@st.cache_data
def process_market_data(response):
    rename_dict = {
        '0x3f4d007982a480dd99052c05d811cf6838ce61b2a2be8dc52fca107f783d1f15': 'ETH+/eUSD',
        '0x461da96754b33fec844fc5e5718bf24298a2c832d8216c5ffd17a5230548f01f': 'WBTC/eUSD',
        '0x6029eea874791e01e2f3ce361f2e08839cd18b1e26eea6243fa3e43fe8f6fa23': 'wstETH/eUSD',
        '0x9ec52d7195bafeba7137fa4d707a0f674a04a6d658c9066bcdbebc6d81eb0011': 'ETH+/WETH',
        '0xf9ed1dba3b6ba1ede10e2115a9554e9c52091c9f1b1af21f9e0fecc855ee74bf': 'bsdETH/eUSD (Base)',
        '0x3a5bdf0be8d820c1303654b078b14f8fc6d715efaeca56cec150b934bdcbff31': 'hyUSD/eUSD (Base)',
        '0xb5d424e4af49244b074790f1f2dc9c20df948ce291fc6bcc6b59149ecf91196d': 'cbETH/eUSD (Base)',
        '0xce89aeb081d719cd35cb1aafb31239c4dfd9c017b2fec26fc2e9a443461e9aea': 'wstETH/eUSD (Base)',
        '0xdf6aa0df4eb647966018f324db97aea09d2a7dde0d3c0a72115e8b20d58ea81f': 'bsdETH/WETH'
    }

    market_data = {}
    bsdETH_price = None
    ETHplus_price = None

    for market in response['markets']['items']:
        if market['uniqueKey'] == '0xf9ed1dba3b6ba1ede10e2115a9554e9c52091c9f1b1af21f9e0fecc855ee74bf':
            bsdETH_price = float(market['collateralPrice']) / 10**36
        if market['uniqueKey'] == '0x3f4d007982a480dd99052c05d811cf6838ce61b2a2be8dc52fca107f783d1f15':
            ETHplus_price = float(market['collateralPrice']) / 10**36

    for market in response['markets']['items']:
        market_name = rename_dict.get(market['uniqueKey'], market['uniqueKey'])
        state = market['state']

        collateral_price = float(market['collateralPrice']) / 10**36
        collateral_assets = float(state['collateralAssets']) / 10**18
        collateral_usd = collateral_price * collateral_assets

        reallocatable_liquidity = float(market['reallocatableLiquidityAssets']) / 10**18

        if market_name == 'bsdETH/WETH':
            reallocatable_liquidity *= bsdETH_price
        if market_name == 'ETH+/WETH':
            reallocatable_liquidity *= ETHplus_price

        market_state = {
            'Collateral USD': int(state['collateralAssetsUsd']) if state['collateralAssetsUsd'] is not None else int(collateral_usd),
            'Total Supply': int(state['supplyAssetsUsd']),
            'Total Borrowed': int(state['borrowAssetsUsd']),
            'Available Liquidity': state['liquidityAssetsUsd'] + reallocatable_liquidity,
            'Utilization': float(state['utilization']),
            'Net Supply APY': float(state['netSupplyApy']),
            'Net Borrow APY': float(state['netBorrowApy']),
            "Reallocatable Liq": reallocatable_liquidity,
            "Direct Liq": int(state['liquidityAssetsUsd']),
        }

        market_data[market_name] = market_state

    df = pd.DataFrame(market_data).T

    if 'bsdETH/WETH' in df.index:
        df.loc['bsdETH/WETH', 'Collateral USD'] *= bsdETH_price

    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].round(4)

    return df




@st.cache_data
def create_borrowers_chart(df, network, is_delta=False):
    y_axis_limit = 120
    
    def color_condition(col):
        return alt.condition(
            alt.datum.Collateral == f'Gauntlet eUSD Core ({col})',
            alt.value('blue'),
            alt.value('red')
        )
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Collateral:N', sort=df['Collateral'].tolist(), axis=alt.Axis(labelAngle=-45), title=network),
        y=alt.Y('Unique Suppliers or Borrowers:Q', title='Open Supply or Borrow Positions', scale=alt.Scale(domain=[0, y_axis_limit])),
        color=color_condition(network),
        tooltip=['Collateral', 'Network', 'Unique Suppliers or Borrowers']
    ).properties(
        width=300,
        height=400
    ).interactive()
    
    return chart


@st.cache_data
def create_market_visualizations(df_market):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_market.index,
        y=df_market['Total Supply'],
        name='Total Supply',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=df_market.index,
        y=df_market['Total Borrowed'],
        name='Total Borrowed',
        marker_color='red'
    ))

    fig.add_trace(go.Bar(
        x=df_market.index,
        y=df_market['Available Liquidity'],
        name='Available Liquidity',
        marker_color='green'
    ))

    fig.update_layout(
        title='Supply, Borrow, and Available Liquidity by Market',
        xaxis_title='Market',
        yaxis_title='USD Value',
        barmode='group',
        xaxis_tickangle=-45
    )

    # Create a pie chart for Total Supply distribution
    fig_supply = px.pie(
        values=df_market['Total Supply'],
        names=df_market.index,
        title='Distribution of Total Supply Across Markets'
    )

    # Create a scatter plot for Utilization vs Net Supply APY
    fig_scatter = px.scatter(
        df_market,
        x='Utilization',
        y='Net Supply APY',
        size='Total Supply',
        color='Net Borrow APY',
        hover_name=df_market.index,
        title='Utilization vs Net Supply APY',
        labels={'Utilization': 'Utilization Rate', 'Net Supply APY': 'Net Supply APY'}
    )

    return fig, fig_supply, fig_scatter

@st.cache_data
def create_liquidations_chart(df_liquidations):
    fig_liquidations = px.bar(
        df_liquidations.groupby('market').agg({'liquidations_total': 'last'}).reset_index(),
        x='market',
        y='liquidations_total',
        title='All-Time Liquidations by Market',
        labels={'liquidations_total': 'Total Liquidations (USD)'}
    )
    return fig_liquidations

# Streamlit app
st.set_page_config(layout="wide")
st.title("Morpho Lending Market Metrics")

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Lazy loading of data
if not st.session_state.data_loaded:
    with st.spinner("Loading market data..."):
        # Fetch and process data
        response_liquidations = fetch_liquidation_data()
        df_liquidations = process_liquidation_data(response_liquidations)

        market_response = fetch_market_data()
        df_market = process_market_data(market_response)

        st.session_state.df_liquidations = df_liquidations
        st.session_state.df_market = df_market
        st.session_state.data_loaded = True

# Display content after data is loaded
if st.session_state.data_loaded:
    # Morpho Borrowers Data
    st.header("Morpho Borrowers Data")

    # Data for borrowers (this is static, so we can keep it as is)
    previous_8_22_data = {
        "Collateral": [
            "Gauntlet eUSD Core (ETH)", "wstETH/eUSD", "WBTC/eUSD", "ETH+/eUSD", "ETH+/WETH",
            "Gauntlet eUSD Core (Base)", "cbETH/eUSD (Base)", "hyUSD/eUSD (Base)", "bsdETH/eUSD (Base)", "wstETH/eUSD (Base)"
        ],
        "Unique Suppliers or Borrowers": [29, 6, 6, 2, 2, 101, 15, 10, 11, 10],
        "Network": ["ETH", "ETH", "ETH", "ETH", "ETH", "Base", "Base", "Base", "Base", "Base"]
    }

    # Data for borrowers as of 8/29
    data = {
        "Collateral": [
            "Gauntlet eUSD Core (ETH)", "wstETH/eUSD", "WBTC/eUSD", "ETH+/eUSD", "ETH+/WETH",
            "Gauntlet eUSD Core (Base)", "cbETH/eUSD (Base)", "hyUSD/eUSD (Base)", "bsdETH/eUSD (Base)", "wstETH/eUSD (Base)"
        ],
        "Unique Suppliers or Borrowers": [35, 7, 6, 5, 2, 112, 12, 21, 13, 8],
        "Network": ["ETH", "ETH", "ETH", "ETH", "ETH", "Base", "Base", "Base", "Base", "Base"]
    }


    # Hard-coded delta data
    delta_data = {
        "Collateral": [
            "Gauntlet eUSD Core (ETH)", "wstETH/eUSD", "WBTC/eUSD", "ETH+/eUSD", "ETH+/WETH",
            "Gauntlet eUSD Core (Base)", "cbETH/eUSD (Base)", "hyUSD/eUSD (Base)", "bsdETH/eUSD (Base)", "wstETH/eUSD (Base)"
        ],
        "Unique Suppliers or Borrowers": [6, 1, 0, 3, 0, 11, -3, 11, 2, -2],
        "Network": ["ETH", "ETH", "ETH", "ETH", "ETH", "Base", "Base", "Base", "Base", "Base"]
    }
    df_previous = pd.DataFrame(previous_8_22_data)
    df_borrowers = pd.DataFrame(data)
    df_delta = pd.DataFrame(delta_data)

    # Split the DataFrame into Mainnet (ETH) and Base
    df_eth = df_borrowers[df_borrowers['Network'] == 'ETH']
    df_base = df_borrowers[df_borrowers['Network'] == 'Base']

    # Display the charts side by side in Streamlit
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Mainnet')
        st.altair_chart(create_borrowers_chart(df_eth, 'ETH'), use_container_width=True)
    with col2:
        st.subheader('Base')
        st.altair_chart(create_borrowers_chart(df_base, 'Base'), use_container_width=True)
    st.subheader('Weekly Change in Open Positions')
    st.altair_chart(create_borrowers_chart(df_delta, 'Weekly Change', is_delta=True), use_container_width=True)

    # Current Markets
    st.header("Current Markets")
    st.dataframe(st.session_state.df_market)

    # Display visualizations
    fig, fig_supply, fig_scatter = create_market_visualizations(st.session_state.df_market)
    st.plotly_chart(fig)
    st.plotly_chart(fig_supply)
    st.plotly_chart(fig_scatter)

    # Morpho Liquidations Section
    st.header("Morpho Liquidations Data")

    st.plotly_chart(create_liquidations_chart(st.session_state.df_liquidations))

    # Dropdown to select a market
    selected_market = st.selectbox(
        "Select a Market to View Liquidations",
        options=st.session_state.df_liquidations['market'].unique()
    )

    # Filter the DataFrame based on the selected market
    filtered_df = st.session_state.df_liquidations[st.session_state.df_liquidations['market'] == selected_market]

    len_liquidations = len(filtered_df)
    st.subheader(f"{len_liquidations} All-Time Liquidation(s) for {selected_market}")
    st.dataframe(filtered_df)

    # Sidebar: Download market data as CSV
    csv = st.session_state.df_market.to_csv(index=True)
    st.sidebar.download_button(
        label="Download Market Data CSV",
        data=csv,
        file_name='morpho_market_data.csv',
        mime='text/csv'
    )

    # Footer
    st.markdown("---")
    st.markdown("Data provided by Morpho Blue API")
else:
    st.info("Loading market data. Please wait...")


from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup the GraphQL client
transport = RequestsHTTPTransport(
    url="https://blue-api.morpho.org/graphql",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Query for Ethereum Mainnet
mainnet_query = gql("""
query {
  vaultPositions(
    first: 500
    orderBy: Shares
    orderDirection: Desc
    where: { vaultAddress_in: ["0xbb819D845b573B5D7C538F5b85057160cfb5f313"] }
  ) {
    items {
      shares
      assets
      assetsUsd
      user {
        address
      }
    }
  }
}
""")

# Query for Base
base_query = gql("""
query {
  vaultPositions(
    first: 500
    orderBy: Shares
    orderDirection: Desc
    where: { vaultAddress_in: ["0xc080f56504e0278828A403269DB945F6c6D6E014"] }
  ) {
    items {
      shares
      assets
      assetsUsd
      user {
        address
      }
    }
  }
}
""")

# Execute queries
mainnet_response = client.execute(mainnet_query)
base_response = client.execute(base_query)

# Count suppliers for Ethereum Mainnet
ethmainnet_suppliers = 0
for item in mainnet_response['vaultPositions']['items']:
    if float(item['assetsUsd']) > 5:
        ethmainnet_suppliers += 1

# Count suppliers for Base
base_suppliers = 0
for item in base_response['vaultPositions']['items']:
    if float(item['assetsUsd']) > 5:
        base_suppliers += 1

# Print the results
print(f"Number of suppliers on Ethereum Mainnet: {ethmainnet_suppliers}")
print(f"Number of suppliers on Base: {base_suppliers}")
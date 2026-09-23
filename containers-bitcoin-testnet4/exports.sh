# Sourced by umbrelOS before rendering this app's compose file, and by any
# app that lists containers-bitcoin-testnet4 under `dependencies:` (e.g.
# containers-electrs-testnet4), so dependents can reach bitcoind directly
# over umbrel_main_network instead of host.docker.internal.

# IP ADDRESSES (10.21.23.0/24 is unused by the official app store)
export APP_CONTAINERS_BITCOIN_TESTNET4_NODE_IP="10.21.23.40"
export APP_CONTAINERS_BITCOIN_TESTNET4_WEB_IP="10.21.23.41"

# PORTS (keep host-published ports outside 40000-49999, which umbrelOS
# reserves for Machines; testnet4's defaults 48332/48333 fall inside it)
export APP_CONTAINERS_BITCOIN_TESTNET4_RPC_PORT="58332"
export APP_CONTAINERS_BITCOIN_TESTNET4_P2P_PORT="58333"

# RPC CREDENTIALS (fixed shared value since v1.2.4; Electrs and any external
# clients configured against it keep working)
export APP_CONTAINERS_BITCOIN_TESTNET4_RPC_USER="umbrel"
export APP_CONTAINERS_BITCOIN_TESTNET4_RPC_PASS="umbrel-electrs-shared-pass"

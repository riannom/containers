# Sourced by umbrelOS before rendering this app's compose file, and by any
# app that lists containers-bitcoin-signet under `dependencies:` (e.g.
# containers-electrs-signet), so dependents can reach bitcoind directly over
# umbrel_main_network instead of host.docker.internal.

# IP ADDRESSES (10.21.23.0/24 is unused by the official app store)
export APP_CONTAINERS_BITCOIN_SIGNET_NODE_IP="10.21.23.10"
export APP_CONTAINERS_BITCOIN_SIGNET_WEB_IP="10.21.23.11"

# PORTS (keep host-published ports outside 40000-49999, which umbrelOS
# reserves for Machines)
export APP_CONTAINERS_BITCOIN_SIGNET_RPC_PORT="38332"
export APP_CONTAINERS_BITCOIN_SIGNET_P2P_PORT="38333"

# RPC CREDENTIALS (fixed shared value since v1.2.4; Electrs and any external
# clients configured against it keep working)
export APP_CONTAINERS_BITCOIN_SIGNET_RPC_USER="umbrel"
export APP_CONTAINERS_BITCOIN_SIGNET_RPC_PASS="umbrel-electrs-shared-pass"

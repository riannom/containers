# Sourced by umbrelOS before rendering this app's compose file, and by any
# app that lists containers-bitcoin-testnet3 under `dependencies:` (e.g.
# containers-electrs-testnet3), so dependents can reach bitcoind directly
# over umbrel_main_network instead of host.docker.internal.

# IP ADDRESSES (10.21.23.0/24 is unused by the official app store)
export APP_CONTAINERS_BITCOIN_TESTNET3_NODE_IP="10.21.23.20"
export APP_CONTAINERS_BITCOIN_TESTNET3_WEB_IP="10.21.23.21"

# PORTS (keep host-published ports outside 40000-49999, which umbrelOS
# reserves for Machines). RPC is not testnet3's default 18332 because the
# official Elements app publishes its P2P port on 18332.
export APP_CONTAINERS_BITCOIN_TESTNET3_RPC_PORT="18335"
export APP_CONTAINERS_BITCOIN_TESTNET3_P2P_PORT="18333"

# RPC CREDENTIALS (fixed shared value since v1.2.4; Electrs and any external
# clients configured against it keep working)
export APP_CONTAINERS_BITCOIN_TESTNET3_RPC_USER="umbrel"
export APP_CONTAINERS_BITCOIN_TESTNET3_RPC_PASS="umbrel-electrs-shared-pass"

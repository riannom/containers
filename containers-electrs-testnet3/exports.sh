# Sourced by umbrelOS before rendering this app's compose file. bitcoind's
# address, ports and RPC credentials come from containers-bitcoin-testnet3's
# exports.sh, which is sourced first because it is listed under
# `dependencies:` in umbrel-app.yml.

# IP ADDRESSES (10.21.23.0/24 is unused by the official app store)
export APP_CONTAINERS_ELECTRS_TESTNET3_IP="10.21.23.22"
export APP_CONTAINERS_ELECTRS_TESTNET3_WEB_IP="10.21.23.23"

# PORTS (keep host-published ports outside 40000-49999, which umbrelOS
# reserves for Machines)
export APP_CONTAINERS_ELECTRS_TESTNET3_PORT="60031"

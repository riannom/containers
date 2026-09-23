# Sourced by umbrelOS before rendering this app's compose file. bitcoind's
# address, ports and RPC credentials come from containers-bitcoin-testnet4's
# exports.sh, which is sourced first because it is listed under
# `dependencies:` in umbrel-app.yml.

# IP ADDRESSES (10.21.23.0/24 is unused by the official app store)
export APP_CONTAINERS_ELECTRS_TESTNET4_IP="10.21.23.42"
export APP_CONTAINERS_ELECTRS_TESTNET4_WEB_IP="10.21.23.43"

# PORTS (keep host-published ports outside 40000-49999, which umbrelOS
# reserves for Machines)
export APP_CONTAINERS_ELECTRS_TESTNET4_PORT="60041"
# Prometheus metrics, reachable only on the app network (not published)
export APP_CONTAINERS_ELECTRS_TESTNET4_METRICS_PORT="4224"

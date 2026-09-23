# Sourced by umbrelOS before rendering this app's compose file. bitcoind's
# address, ports and RPC credentials come from containers-bitcoin-signet's
# exports.sh, which is sourced first because it is listed under
# `dependencies:` in umbrel-app.yml.

# IP ADDRESSES (10.21.23.0/24 is unused by the official app store)
export APP_CONTAINERS_ELECTRS_SIGNET_IP="10.21.23.12"
export APP_CONTAINERS_ELECTRS_SIGNET_WEB_IP="10.21.23.13"

# PORTS (keep host-published ports outside 40000-49999, which umbrelOS
# reserves for Machines)
export APP_CONTAINERS_ELECTRS_SIGNET_PORT="60051"
# Prometheus metrics, reachable only on the app network (not published)
export APP_CONTAINERS_ELECTRS_SIGNET_METRICS_PORT="4224"

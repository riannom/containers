# Sourced by umbrelOS before rendering this app's compose file, and by any
# app that lists containers-bitcoin-testnet3 under `dependencies:` (e.g.
# containers-electrs-testnet3), so dependents can reach bitcoind directly over
# umbrel_main_network instead of host.docker.internal.

# --- host port picker (identical in every app's exports.sh; source of truth:
# tools/port-picker.sh, installed by tools/sync-port-picker.py) -------------
# umbrelOS sources exports.sh as root under `set -euo pipefail` before every
# install, start and update, and dependent apps source it too, so this must
# never fail or print anything.
#
# Each published host port is chosen the first time the app is set up and
# remembered in ports.env in the app's data directory. The default is used
# unless another installed app claims it (exports, compose ports or dashboard
# port) or something already listens on it; then default+100, +200, ... are
# tried, skipping 40000-49999 (reserved by umbrelOS for Machines). A
# remembered port is only given up if another installed app claims it later.
# Ports held by this app's own running containers don't count as in use.
containers_pick_port() {
  local key="${1}" default="${2}"
  local dir="${EXPORTS_APP_DIR:-}"
  if [[ -z "${dir}" || ! -d "${dir}" ]]; then printf '%s' "${default}"; return 0; fi
  local state="${dir}/ports.env" apps_dir d
  apps_dir="$(dirname "${dir}")"
  local -a others=()
  for d in "${apps_dir}"/*/; do
    d="${d%/}"
    [[ -d "${d}" && "${d}" != "${dir%/}" ]] && others+=("${d}")
  done
  local claimed="" listening="" saved="" k p
  if (( ${#others[@]} )); then
    claimed="$( {
      cat "${others[@]/%//exports.sh}" | grep -oE '_PORT="?[0-9]{2,5}"?'
      cat "${others[@]/%//ports.env}" | grep -oE '^[A-Z_]+=[0-9]{2,5}$'
      cat "${others[@]/%//docker-compose.yml}" | grep -oE '^[[:space:]]*-[[:space:]]*"?[0-9]{2,5}:'
      cat "${others[@]/%//umbrel-app.yml}" | grep -oE '^port:[[:space:]]*[0-9]{2,5}'
    } 2>/dev/null | grep -oE '[0-9]{2,5}' | sort -u || true )"
  fi
  listening="$(ss -Htln 2>/dev/null | awk '{n = split($4, a, ":"); print a[n]}' | sort -u || true)"
  # Ports published by this app's own containers are not a conflict (e.g. if
  # exports are sourced while the app is running and ports.env is missing).
  local own
  own="$(docker ps --filter "label=com.docker.compose.project=$(basename "${dir}")" --format '{{.Ports}}' 2>/dev/null \
    | grep -oE ':[0-9]+(-[0-9]+)?->' | tr -d ':>' | tr -- '-' ' ' \
    | awk '{e = ($2 == "") ? $1 : $2; for (i = $1; i <= e; i++) print i}' | sort -u || true)"
  if [[ -n "${own}" ]]; then listening="$(grep -vxF -f <(printf '%s\n' "${own}") <<< "${listening}" || true)"; fi
  if [[ -f "${state}" ]]; then
    saved="$(grep -E "^${key}=[0-9]+$" "${state}" 2>/dev/null | tail -n 1 | cut -d= -f2 || true)"
  fi
  if [[ -n "${saved}" ]] && ! grep -qx "${saved}" <<< "${claimed}"; then
    printf '%s' "${saved}"; return 0
  fi
  for (( k = 0; k <= 40; k++ )); do
    p=$(( default + 100 * k ))
    if (( p > 65535 )); then break; fi
    if (( p >= 40000 && p <= 49999 )); then continue; fi
    if grep -qx "${p}" <<< "${claimed}" || grep -qx "${p}" <<< "${listening}"; then continue; fi
    { grep -vE "^${key}=" "${state}" 2>/dev/null || true; printf '%s=%s\n' "${key}" "${p}"; } > "${state}.tmp" 2>/dev/null \
      && mv -f "${state}.tmp" "${state}" 2>/dev/null || true
    printf '%s' "${p}"; return 0
  done
  printf '%s' "${default}"
}
# --- end host port picker ---------------------------------------------------

# IP ADDRESSES (10.21.23.0/24 is unused by the official app store)
export APP_CONTAINERS_BITCOIN_TESTNET3_NODE_IP="10.21.23.20"
export APP_CONTAINERS_BITCOIN_TESTNET3_WEB_IP="10.21.23.21"

# PORTS (published on the host; see the port picker above)
export APP_CONTAINERS_BITCOIN_TESTNET3_RPC_PORT="$(containers_pick_port RPC_PORT 18332)"
export APP_CONTAINERS_BITCOIN_TESTNET3_P2P_PORT="$(containers_pick_port P2P_PORT 18333)"

# RPC CREDENTIALS (fixed shared value since v1.2.4; Electrs and any external
# clients configured against it keep working)
export APP_CONTAINERS_BITCOIN_TESTNET3_RPC_USER="umbrel"
export APP_CONTAINERS_BITCOIN_TESTNET3_RPC_PASS="umbrel-electrs-shared-pass"

unset -f containers_pick_port

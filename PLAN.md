# Plan: Umbrel community store with Bitcoin Core testnet3 / testnet4 / signet containers

## Goal
Publish three Umbrel community-store apps that run Bitcoin Core on, respectively,
testnet3, testnet4 and signet — installable via the community store at
`https://github.com/riannom/containers`. Data directories must be isolated so
they cannot collide with the official mainnet `bitcoind` app from the main
Umbrel store.

## Decisions (already confirmed)
- Bitcoin Core image: `bitcoin/bitcoin` (official Docker Hub image).
- Community-store id: `containers` (matches repo name).
- RPC exposure: each container publishes its RPC port on the host on a
  network-specific port so other apps / tooling can connect.
- Reference for repo layout only: `riannom/rh-containers`. No bitcoind
  configuration is being copied from elsewhere.

## Repository layout
```
containers/
├── umbrel-app-store.yml             # id: containers, name: Containers
├── PLAN.md                          # this file
├── containers-bitcoin-testnet3/
│   ├── umbrel-app.yml
│   ├── docker-compose.yml
│   └── icon.svg
├── containers-bitcoin-testnet4/
│   ├── umbrel-app.yml
│   ├── docker-compose.yml
│   └── icon.svg
└── containers-bitcoin-signet/
    ├── umbrel-app.yml
    ├── docker-compose.yml
    └── icon.svg
```

The directory prefix `containers-` is required by Umbrel: every app id in a
community store must start with the store id.

## Per-network configuration

| Network   | `-chain=` value | P2P (host) | RPC (host) | Subdir under datadir |
|-----------|-----------------|------------|------------|----------------------|
| testnet3  | `test`          | 18333      | 18332      | `testnet3/`          |
| testnet4  | `testnet4`      | 48333      | 48332      | `testnet4/`          |
| signet    | `signet`        | 38333      | 38332      | `signet/`            |

Mainnet bitcoind uses 8333/8332, so none of these collide. Each container is
its own Umbrel app, so each gets its own `${APP_DATA_DIR}` (e.g.
`~/umbrel/app-data/containers-bitcoin-testnet3/`) — fully isolated from the
mainnet `bitcoind` app's data dir.

## docker-compose.yml shape (per container)
Each app reuses the official Umbrel Bitcoin dashboard image
`ghcr.io/getumbrel/umbrel-bitcoin:v1.2.2`, which bundles bitcoind +
the Home / Insight / Settings web UI in one container.

- `app_proxy` service routing to the dashboard's port `3000` so that
  clicking the app icon in Umbrel opens the UI.
- `app` service running the dashboard image:
  - `user: "1000:1000"`, `restart: on-failure`, `stop_grace_period: 15m30s`.
  - Volume: `${APP_DATA_DIR}/data:/data` (the image expects `/data` as the
    root of its app + bitcoin state, not `/data/.bitcoin`).
  - Ports: P2P + RPC published as in the table above.
  - Static IP `10.21.21.8` on a per-app `10.21.21.0/24` bridge network
    (matches the upstream prod compose's IP plumbing). Each Umbrel app is
    in its own docker network namespace, so the same subnet can be reused
    across all three testnet apps with no cross-app collision.
  - Environment:
    - `DEFAULT_CHAIN: test | testnet4 | signet` — sets the chain on first
      launch; the user can later change it from the Settings tab.
    - `BITCOIND_EXTRA_ARGS: '-deprecatedrpc=create_bdb'` — matches the
      official mainnet app.
    - `P2P_PORT` / `RPC_PORT` — the host-published ports for that network.
    - `BITCOIND_IP: 10.21.21.8` — used both for bitcoind's `rpcbind`/`bind`
      and as the connect host for the dashboard's RPC client (same
      container, reachable on its own static IP).
    - `RPC_USER: umbrel`, `RPC_PASS: ${APP_PASSWORD}` — Umbrel injects the
      per-app random secret.
    - `TOR_HOST` / `I2P_HOST` set to dummy in-subnet IPs (`10.21.21.10` /
      `10.21.21.11`) so the bitcoin.conf template renders cleanly even
      though no Tor or I2P sidecar is deployed; bitcoind will simply log
      that those proxies are unreachable and fall through to clearnet.
    - Internal-only ports (Tor 8334, P2P whitebind 8335, ZMQ 28332-28336)
      reuse the same numbers as the mainnet app — they live inside each
      app's isolated network and do not collide.

### Why the official dashboard image instead of `bitcoin/bitcoin`
- Replaces a manually-rolled headless setup with the same Home / Insight /
  Settings UI as the official Umbrel Bitcoin app.
- The image bundles bitcoind v30.2 (default), v30.0, and v29.2; the
  dashboard's Settings tab can switch between bundled versions. All three
  support `-chain=testnet4`.
- Source code: <https://github.com/getumbrel/umbrel-bitcoin>. Confirmed
  via the backend's `config.ts` that `DEFAULT_CHAIN` natively accepts
  `test`, `testnet4`, and `signet`.

### What we trade away
- We no longer pin `bitcoin/bitcoin:<version>`; the bitcoind binary is
  whatever the dashboard image ships.
- Tor and I2P sidecars are not deployed; those tabs in the dashboard show
  as unreachable. Easy to add later if the use case calls for it.

## umbrel-app.yml shape (per container)
Manifest fields, mirroring the structure seen in `rh-containers` but written
fresh for each network:
- `manifestVersion: 1.1`
- `id` = directory name
- `name`: e.g. "Bitcoin testnet4"
- `tagline`: short, network-specific
- `category: bitcoin`
- `icon`: raw GitHub URL to the per-container `icon.svg`
- `version`: matches the dashboard image (`1.2.2`), since that is what
  users see updates against — not the bundled bitcoind version.
- `port: 3000` — the dashboard UI port (the `app_proxy` routes here).
- `description`: 2–3 sentences explaining the network, mentioning that the
  dashboard is included, and that this app does not affect or share data
  with the mainnet bitcoind app.
- `website`, `support`, `repo`: this repo
- `developer: riannom`

## icon.svg
Three simple 1024×1024 SVGs — the Bitcoin "₿" glyph plus a network label
(TESTNET3 / TESTNET4 / SIGNET). Distinct accent colors per network so they
are easy to tell apart in the Umbrel store grid:
- testnet3: green
- testnet4: blue
- signet: purple

## Steps to execute
1. Verify `bitcoin/bitcoin` tags on Docker Hub and pin a concrete version
   that supports testnet4 (likely `28.1`).
2. Write `umbrel-app-store.yml`.
3. For each of the three networks, write `umbrel-app.yml`,
   `docker-compose.yml`, and `icon.svg`.
4. `git add` + initial commit on `main`.
5. Push to `origin/main` (`https://github.com/riannom/containers`) — confirm
   with the user before pushing.

## Open items
- Confirm a Bitcoin Core image tag to pin (default proposal: `28.1`).
- Decide whether to enable `-txindex=1`. Default: off (smaller, faster).
- Whether to also publish ZMQ ports. Default: not yet — easy to add later.

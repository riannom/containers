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
- Single service `server` running `bitcoin/bitcoin:<pinned-version>`.
- `restart: unless-stopped`, `stop_grace_period: 5m` so bitcoind can flush.
- Volume: `${APP_DATA_DIR}/data:/data/.bitcoin`.
- Ports: P2P + RPC published as in the table above.
- Command-line args (rather than mounting a `bitcoin.conf`):
  - `-chain=<network>`
  - `-datadir=/data/.bitcoin`
  - `-server=1`
  - `-rpcbind=0.0.0.0`
  - `-rpcallowip=10.0.0.0/8` and `172.16.0.0/12` (cover Umbrel's docker
    networks; not `0.0.0.0/0` so we don't accidentally expose RPC to LAN
    even if firewalling slips).
  - `-rpcuser=umbrel`
  - `-rpcpassword=${APP_PASSWORD}` (Umbrel injects a per-app random secret;
    falls back to a placeholder we'll document in releaseNotes if absent).
  - `-rpcport=<network rpc port>`
  - `-port=<network p2p port>`
- No `app_proxy` service: these apps have no web UI; they are backend
  services. `port` in `umbrel-app.yml` is set to the RPC port purely to
  satisfy the manifest schema.

### Why `bitcoin/bitcoin` and `-chain=` flags
- The image is the upstream-maintained Bitcoin Core build; entrypoint is
  `bitcoind`, so CLI args are passed via compose `command:`.
- `-chain=testnet4` requires Bitcoin Core ≥ 28.0; we'll pin to a version
  that supports it (proposed: `28.1`). Verify the tag exists on Docker Hub
  before writing the compose files.

## umbrel-app.yml shape (per container)
Manifest fields, mirroring the structure seen in `rh-containers` but written
fresh for each network:
- `manifestVersion: 1.1`
- `id` = directory name
- `name`: e.g. "Bitcoin testnet4"
- `tagline`: short, network-specific
- `category: bitcoin`
- `icon`: raw GitHub URL to the per-container `icon.svg`
- `version`: matches pinned Bitcoin Core version
- `port`: the RPC host port for that network
- `description`: 2–3 sentences explaining the network and that this app does
  not affect or share data with the mainnet bitcoind app.
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

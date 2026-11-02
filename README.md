# Bitcoin test-network containers

Umbrel community apps for Bitcoin Core and Electrs on testnet3, testnet4,
and signet. Each app has its own data directory and host ports.

The primary repository is https://forgejo.tabineko.dev/nekoguntai-castle/containers.
The GitHub copy is https://github.com/riannom/containers. This checkout is
configured to push to both; that local Git configuration is not inherited by
new clones and is not a server-side mirror.

## Bitcoin Core update policy

Track the latest **stable** Bitcoin Core release and incorporate its fixes by
updating the bundled binary through the upstream Umbrel Bitcoin image. We do
not build Bitcoin Core from its development branch or maintain a Core patch fork.

As checked on 2026-11-01:

- Bitcoin Core stable: [32.1](https://github.com/bitcoin/bitcoin/releases/tag/v32.1).
- Dashboard image: `ghcr.io/getumbrel/umbrel-bitcoin:v1.5.0`, pinned to the
  multi-platform digest `sha256:2bf5f6c1612abcbd050bef98f839ee3489f589bb46fbb50fd5f0340d9cc1bd3c`.
- The [upstream Dockerfile](https://github.com/getumbrel/umbrel-bitcoin/blob/v1.5.0/apps/backend/Dockerfile)
  bundles Core 32.1 as its default and also includes older selectable versions.

An image update does not override a user's explicit Core version selection.
For existing installs, select **Always use the latest version** in the dashboard
settings to run the newest bundled Core. Verify the running daemon with
`bitcoin-cli getnetworkinfo` inside the node container; Core 32.1 reports
`version: 320100`. A newer image alone does not prove an existing node uses
that version.

## Updating all three apps

1. Check Bitcoin Core's latest stable release and release notes, including
   compatibility changes for test networks, RPC clients, indexes, and wallets.
2. Find a released Umbrel Bitcoin image that bundles that Core version. Check
   its tagged source and registry manifest for both amd64 and arm64 support.
   If Umbrel has not shipped it, record the gap; do not describe the existing
   image as containing all current stable fixes.
3. Update the same tag and multi-platform digest in all three
   `containers-bitcoin-*/docker-compose.yml` files. Bump the three
   `umbrel-app.yml` versions and write upgrade notes, including any required
   action for existing pinned versions.
4. Validate Compose interpolation with the app's exports and Umbrel environment.
   In disposable data directories, test dashboard startup, Core version,
   authenticated RPC, and network selection on all three networks. Check
   existing-version settings and Electrs compatibility before deployment.
5. Update this version record, review the diff, and push the validated change.
   Installed Umbrel apps must still be updated to deploy it. Verify their
   actual running versions afterward.

Image pins are deliberately immutable. Future upstream releases require another
reviewed update; this repository currently has no automatic release monitor.

`PLAN.md` is historical design context and contains superseded implementation
choices; the Compose files and app manifests define the current apps.

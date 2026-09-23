# Generates every app icon. Each app type has one shared design; the network
# is shown by its colours and a corner badge (S, 3 or 4). Glyphs and the
# bitcoin symbol are stroked paths, not font text, so they render the same
# everywhere. Run from the repo root: python3 tools/generate-icons.py
# The Electrs status page (index.html.template) draws the Electrs mark inline;
# keep its markSvg() in sync when changing electrs_mark().
NETS = {
    "signet":   dict(bg=("#241040", "#0a0612"), mark=("#f3e8ff", "#a855f7"), glow="#a855f7"),
    "testnet3": dict(bg=("#0a3321", "#040d09"), mark=("#dcfce7", "#22c55e"), glow="#22c55e"),
    "testnet4": dict(bg=("#0d2552", "#050a16"), mark=("#dbeafe", "#3b82f6"), glow="#3b82f6"),
}
# Badge glyphs, ~100x150, centred on (0,0).
GLYPHS = {
    "signet":   "M 40 -48 C 30 -74 -42 -76 -42 -36 C -42 -4 42 -6 42 32 C 42 74 -30 76 -44 46",
    "testnet3": "M -40 -52 C -24 -78 42 -76 40 -36 C 38 -10 12 -6 -6 -6 C 22 -6 46 6 44 34 C 42 74 -22 78 -44 52",
    "testnet4": "M 26 72 V -72 L -48 30 H 52",
}
BADGE = (736, 736, 132)

# Bitcoin: the bitcoin logo, a tilted B-with-strokes knocked out of a disc.
BITCOIN_SYMBOL = ("M 356 316 V 628 M 356 316 H 486 C 546 316 566 350 566 390 C 566 432 540 462 486 462 H 356 "
                  "M 356 462 H 504 C 566 462 588 500 588 546 C 588 596 556 628 496 628 H 356 "
                  "M 396 250 V 316 M 456 250 V 316 M 396 628 V 694 M 456 628 V 694 M 324 316 H 356 M 324 628 H 356")

def bitcoin_mark(c):
    return [
        '  <circle cx="472" cy="472" r="240" fill="url(#mark)"/>',
        # Scale the symbol (bbox centre 456,472) to sit inside the disc, then tilt it.
        f'  <path transform="rotate(14 472 472) translate(472 472) scale(0.68) translate(-456 -472)" d="{BITCOIN_SYMBOL}" fill="none" stroke="{c["bg"][1]}" stroke-width="60" stroke-linecap="round" stroke-linejoin="round"/>',
    ]

# Electrs: a stack of three server slabs (the index), outlined.
def electrs_mark(c):
    out = []
    for i in range(3):
        y = 293 + i * 140
        out.append(f'  <rect x="288" y="{y}" width="368" height="78" rx="39" fill="none" stroke="url(#mark)" stroke-width="32"/>')
        out.append(f'  <circle cx="348" cy="{y + 39}" r="17" fill="url(#mark)"/>')
        out.append(f'  <path d="M 540 {y + 39} H 596" stroke="url(#mark)" stroke-width="20" stroke-linecap="round"/>')
    return out

def icon(net, kind):
    c = NETS[net]; bx, by, br = BADGE
    body = bitcoin_mark(c) if kind == "bitcoin" else electrs_mark(c)
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">',
        '  <defs>',
        f'    <linearGradient id="bg" x1="0" y1="0" x2="1024" y2="1024" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{c["bg"][0]}"/><stop offset="1" stop-color="{c["bg"][1]}"/></linearGradient>',
        f'    <linearGradient id="mark" x1="232" y1="232" x2="792" y2="792" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{c["mark"][0]}"/><stop offset="1" stop-color="{c["mark"][1]}"/></linearGradient>',
        f'    <radialGradient id="glow" cx="512" cy="512" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{c["glow"]}" stop-opacity="0.28"/><stop offset="1" stop-color="{c["glow"]}" stop-opacity="0"/></radialGradient>',
        '  </defs>',
        '  <rect width="1024" height="1024" fill="url(#bg)"/>',
        '  <rect width="1024" height="1024" fill="url(#glow)"/>',
        *body,
        f'  <circle cx="{bx}" cy="{by}" r="{br}" fill="url(#mark)" stroke="url(#bg)" stroke-width="36"/>',
        f'  <path transform="translate({bx} {by})" d="{GLYPHS[net]}" fill="none" stroke="{c["bg"][1]}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>',
        '</svg>',
    ]) + "\n"

if __name__ == "__main__":
    for net in NETS:
        for kind in ("bitcoin", "electrs"):
            open(f"containers-{kind}-{net}/icon.svg", "w").write(icon(net, kind))

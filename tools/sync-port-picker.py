# Copies tools/port-picker.sh into every app's exports.sh (between the
# "--- host port picker" and "--- end host port picker" marker lines).
# Each app directory ships on its own, so the block has to be duplicated.
# Run from the repo root: python3 tools/sync-port-picker.py
import glob, re

block = open("tools/port-picker.sh").read().rstrip("\n") + "\n"
pattern = re.compile(r"# --- host port picker.*?# --- end host port picker -+\n", re.S)
for path in sorted(glob.glob("containers-*/exports.sh")):
    text = open(path).read()
    if not pattern.search(text):
        raise SystemExit(f"{path}: marker block not found")
    open(path, "w").write(pattern.sub(lambda _: block, text, count=1))
    print("synced", path)

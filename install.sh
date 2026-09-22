#!/usr/bin/env sh
# Install ruleprune so it can be run as `ruleprune` from anywhere on the system.
#
# It symlinks ruleprune.py into a directory on your PATH. Because it is a
# symlink, `git pull` in this repo updates the installed command automatically
# -- no need to re-run the installer after an update.
set -eu

SRC_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC="$SRC_DIR/ruleprune.py"

if [ ! -f "$SRC" ]; then
    echo "Cannot find ruleprune.py next to this installer." >&2
    exit 1
fi

chmod +x "$SRC"

# Prefer a system-wide location when we can write to it; otherwise fall back to
# the per-user bin directory.
if [ -w /usr/local/bin ] 2>/dev/null; then
    DEST_DIR=/usr/local/bin
elif [ "$(id -u)" = "0" ]; then
    DEST_DIR=/usr/local/bin
    mkdir -p "$DEST_DIR"
else
    DEST_DIR="$HOME/.local/bin"
    mkdir -p "$DEST_DIR"
fi

DEST="$DEST_DIR/ruleprune"
ln -sf "$SRC" "$DEST"
echo "Linked $DEST -> $SRC"

# Warn if the chosen directory is not on PATH yet.
case ":$PATH:" in
    *":$DEST_DIR:"*) ;;
    *)
        echo ""
        echo "NOTE: $DEST_DIR is not on your PATH."
        echo "Add this line to your shell profile (~/.bashrc, ~/.zshrc, ...):"
        echo "    export PATH=\"$DEST_DIR:\$PATH\""
        ;;
esac

echo "Done. Start a new shell (or re-source your profile), then run: ruleprune"

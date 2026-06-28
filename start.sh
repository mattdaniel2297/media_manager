#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC}  $*"; }
warn() { echo -e "  ${YELLOW}!${NC}  $*"; }
fail() { echo -e "  ${RED}✗${NC}  $*"; }
fix()  { echo -e "     ${YELLOW}→${NC} $*"; }

errors=0

echo ""
echo -e "${BOLD}Media Manager — Startup Check${NC}"
echo ""
echo "System dependencies:"

# python3
if command -v python3 &>/dev/null; then
    ok "$(python3 --version)"
else
    fail "python3 not found"
    fix "sudo apt install python3"
    errors=$((errors + 1))
fi

# python3-venv
if python3 -c "import venv" 2>/dev/null; then
    ok "python3-venv"
else
    fail "python3-venv not found"
    fix "sudo apt install python3-venv python3-full"
    errors=$((errors + 1))
fi

# pyexiv2 — must come from apt (native extension linking libexiv2)
if python3 -c "import pyexiv2" 2>/dev/null; then
    ok "python3-py3exiv2"
else
    fail "python3-py3exiv2 not found"
    fix "sudo apt install python3-py3exiv2"
    errors=$((errors + 1))
fi

# TrueType font for watermark (warning only — fallback exists)
FONT_FOUND=""
for f in \
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf" \
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" \
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
do
    if [ -f "$f" ]; then
        FONT_FOUND="$f"
        break
    fi
done

if [ -n "$FONT_FOUND" ]; then
    ok "Font: $(basename "$FONT_FOUND")"
else
    warn "No preferred TrueType font found — watermark will use fallback bitmap font"
    fix "sudo apt install fonts-ubuntu   # or: fonts-dejavu-core"
fi

echo ""

if [ "$errors" -gt 0 ]; then
    if [ "$errors" -eq 1 ]; then dep="dependency"; else dep="dependencies"; fi
    echo -e "${RED}${BOLD}${errors} system ${dep} missing.${NC} Install above and re-run."
    echo ""
    exit 1
fi

# Virtual environment
echo "Virtual environment:"
if [ ! -d "$VENV_DIR" ]; then
    echo -n "  Creating .venv (with system-site-packages) ..."
    python3 -m venv --system-site-packages "$VENV_DIR"
    echo -e " ${GREEN}done${NC}"
else
    ok ".venv exists"
fi

# Pip packages
echo ""
echo "Pip packages:"
"$VENV_DIR/bin/pip" install --quiet flask pillow
ok "flask, pillow"

echo ""
echo -e "${GREEN}${BOLD}All checks passed.${NC} Starting on http://127.0.0.1:5000"
echo ""

exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/app.py"

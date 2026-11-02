#!/usr/bin/env bash
# Recalculate an xlsxwriter workbook with headless LibreOffice so cached values exist (for QA reads).
# Usage: pipeline/recalc.sh <in.xlsx> <outdir> [profile_dir]
set -euo pipefail
IN="$1"; OUT="$2"; PROF="${3:-${TMPDIR:-/tmp}/lo_recalc_profile}"
mkdir -p "$PROF/user" "$OUT"
cat > "$PROF/user/registrymodifications.xcu" <<'XCU'
<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
XCU
timeout 240 libreoffice -env:UserInstallation=file://"$PROF" --headless --calc --convert-to xlsx --outdir "$OUT" "$IN" >/dev/null 2>&1

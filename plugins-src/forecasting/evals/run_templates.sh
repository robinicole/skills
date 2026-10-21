#!/usr/bin/env bash
# Run every template end to end in a scratch folder. Logs and plots go to evals/runs/templates/.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(dirname "$HERE")"
PYTHON="${PYTHON:-python3}"
OUT="$HERE/runs/templates"
WORK="$(mktemp -d)"
mkdir -p "$OUT"
cp "$PLUGIN"/templates/*.py "$WORK"/
export FC_OUT="$OUT/plots" FPP_DATA_CACHE="${FPP_DATA_CACHE:-$HOME/.cache/fpp_data}" MPLBACKEND=Agg
fail=0
for t in baselines explore regression ets arima dynamic_regression hierarchical advanced practical simulate audit_checks; do
  start=$(date +%s)
  if (cd "$WORK" && "$PYTHON" -W ignore "$t.py" > "$OUT/$t.log" 2>&1); then
    echo "PASS $t ($(( $(date +%s) - start ))s)"
  else
    echo "FAIL $t (see $OUT/$t.log)"; fail=1
  fi
done
rm -rf "$WORK"
exit $fail

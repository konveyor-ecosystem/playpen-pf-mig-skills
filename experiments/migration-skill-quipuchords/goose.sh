#!/bin/bash
set -euo pipefail

LOGFILE="${LOGFILE:-migration-$(date +%Y%m%d-%H%M%S).log}"

echo "Starting migration at $(date)" | tee "$LOGFILE"
echo "Log file: $LOGFILE" | tee -a "$LOGFILE"
echo "---" | tee -a "$LOGFILE"

time goose run --recipe ../../goose/recipes/migration.yaml \
--params source_tech="PatternFly 5" \
--params target_tech="PatternFly 6" \
--params input_path="./quipucords-ui" \
--params workspace_dir="./workdir" \
--params rules="./rulesets" \
2>&1 | tee -a "$LOGFILE" 


EXIT_CODE=${PIPESTATUS[0]}
echo "---" | tee -a "$LOGFILE"
echo "Finished at $(date) with exit code: $EXIT_CODE" | tee -a "$LOGFILE"
exit $EXIT_CODE

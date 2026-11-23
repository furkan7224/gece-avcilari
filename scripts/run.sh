#!/usr/bin/env bash
# Her adımın çıktısını günlüğe de yazar
bash --noprofile --norc -eo pipefail "$1" 2>&1 | tee -a "${RUNNER_TEMP:-/tmp}/log.txt"
exit "${PIPESTATUS[0]}"

#!/usr/bin/env bash
set -euo pipefail
source /vgg/yushi/miniconda3/etc/profile.d/conda.sh
conda activate th29py312
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_ROOT="${WEB_ROOT:-/scratch/shared/engs2907/open-source/holo4d/project-page-media_20261009}"
SELECTED_ROOT="${SELECTED_ROOT:-/scratch/shared/engs2907/logs/track4d-360/project_page/selected_filtered_20261011}"
LONG_PICKS="${LONG_PICKS:-/scratch/shared/engs2907/open-source/holo4d/project-page-review_20261011/robot_long_picks_motion_review.json}"
python "$PAGE_ROOT/tools/curate_web_media.py" --selected-root "$SELECTED_ROOT" --long-picks "$LONG_PICKS" --expected-selected "${EXPECTED_SELECTED:-80}" --output "$WEB_ROOT/curation.json"
python "$PAGE_ROOT/tools/export_web_media.py" --manifest "$WEB_ROOT/curation.json" --output "$WEB_ROOT" --workers "${WEB_WORKERS:-2}" "$@"

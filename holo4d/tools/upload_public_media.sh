#!/usr/bin/env bash
# Publish only the already-audited compact media, not the private export cache.
# Run on a compute node. No source predictions or private JSON are uploaded.
set -euo pipefail
source /vgg/yushi/miniconda3/etc/profile.d/conda.sh
conda activate th29py312
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
hf upload yslan/Holo4D-2026 \
  /scratch/shared/engs2907/open-source/holo4d/project-page-release_20261012_compact/static/videos/web \
  project_page/media_20261012 --repo-type model \
  --include '*.mp4' --include '*.jpg' \
  --commit-message 'Publish compact Holo4D project-page videos and lazy posters'

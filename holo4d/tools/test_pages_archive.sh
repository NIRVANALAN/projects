#!/usr/bin/env bash
# Reproduce Pages' dereferencing archive on a clean tracked-file checkout.
# Keep the diagnostic staging directory; never delete original cache media.
set -euo pipefail
cd /vgg/yushi/Repo/websites/projects
stage=$(mktemp -d /scratch/shared/engs2907/open-source/holo4d/pages-archive-check.XXXXXX)
git archive HEAD | tar -x -C "$stage"
tar --dereference --hard-dereference --directory "$stage" -cf /dev/null .
echo "Pages archive passed for $(git rev-parse HEAD); staging=$stage"

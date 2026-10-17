"""Materialize small, same-origin JPEG covers; never copy or alter inference RGB."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import os
import tempfile

from audit_storage import required_files


def prepare(page_root, refresh=False):
    media = page_root / 'static/videos/web'
    output = page_root / 'static/posters/web'
    required = sorted(p for p in required_files(page_root) if p.suffix == '.jpg')
    report = []
    for relative in required:
        source, target = media / relative, output / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        matches = target.is_file() and not target.is_symlink() and hashlib.sha256(target.read_bytes()).hexdigest() == digest
        if target.exists() and not matches and not refresh:
                raise ValueError(f'Refusing to replace a different existing cover: {target}')
        if not matches:
            target.parent.mkdir(parents=True, exist_ok=True)
            handle, name = tempfile.mkstemp(prefix='.poster-', dir=target.parent)
            os.close(handle)
            try:
                shutil.copy2(source, name, follow_symlinks=True)
                os.replace(name, target)
            finally:
                Path(name).unlink(missing_ok=True)
        report.append(dict(path=str(relative), bytes=target.stat().st_size, sha256=digest))
    return dict(status='passed', count=len(report), bytes=sum(r['bytes'] for r in report), covers=report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--refresh', action='store_true', help='Refresh derived covers that differ from the current export')
    args = parser.parse_args()
    report = prepare(args.page_root, args.refresh)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'covers'}))


if __name__ == '__main__':
    main()

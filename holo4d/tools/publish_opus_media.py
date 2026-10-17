"""Publish only absent Task A/B files and verify anonymous playback ranges.

Never modifies website files or overwrites existing HF objects. Run on compute.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from huggingface_hub import CommitOperationAdd, HfApi

REPO = 'yslan/Holo4D-2026'
PREFIX = 'project_page/media_20261012'
OLD_REVISION = 'd961d338edf61d0f3e2786e4ced60be69c02bcda'


def atomic_json(path, payload):
    tmp = path.with_suffix('.pending.json')
    tmp.write_text(json.dumps(payload,indent=2)+'\n')
    tmp.replace(path)


def inventory(api, revision):
    return {entry.path:entry.blob_id for entry in api.list_repo_tree(REPO,path_in_repo=PREFIX,
        revision=revision,recursive=True) if hasattr(entry,'blob_id')}


def probe_url(item):
    path,revision = item
    url=f'https://huggingface.co/{REPO}/resolve/{revision}/{quote(path)}'
    movie=path.endswith('.mp4')
    request=Request(url,headers={'Range':'bytes=0-1023'} if movie else {})
    with urlopen(request,timeout=40) as response:
        content=response.read(1024 if movie else 200000)
        result=dict(path=path,status=response.status,type=response.headers.get('Content-Type'),bytes_read=len(content))
        if result['status'] != (206 if movie else 200):
            raise ValueError(f'Wrong anonymous status: {result}')
        if movie and (not result['type'].startswith('video/mp4') or len(content)!=1024):
            raise ValueError(f'Invalid video range: {result}')
        return result


def publish(root):
    records=json.loads((root/'media_manifest.json').read_text())['records']
    validation=json.loads((root/'decoded_validation.json').read_text())
    if validation.get('status') != 'passed' or validation.get('videos') != 15:
        raise ValueError('All15 videos must pass decoded validation before upload')
    payload=root/'payload'
    files=sorted(p for p in payload.rglob('*') if p.is_file())
    expected={f'{PREFIX}/{r[key]}' for r in records for key in ['path','poster']}
    actual={str(p.relative_to(payload)) for p in files}
    if len(records)!=15 or len(files)!=30 or actual != expected:
        raise ValueError('Upload must contain precisely15new MP4s and15new posters, no provenance')
    for record in records:
        digest=hashlib.sha256((payload/PREFIX/record['path']).read_bytes()).hexdigest()
        if digest != record['output_sha256']:
            raise ValueError('Payload changed after validation')
    api=HfApi()
    report_path=root/'hf_upload.json'
    if report_path.exists():
        report=json.loads(report_path.read_text())
        if report['new_files'] != sorted(actual):
            raise ValueError('Resume report differs from the approved payload')
    else:
        parent=api.model_info(REPO).sha
        existing=set(api.list_repo_files(REPO,revision=parent))
        overlap=actual & existing
        if overlap:
            raise FileExistsError(f'Add-only upload refused; paths already exist: {sorted(overlap)}')
        original=inventory(api,OLD_REVISION)
        operations=[CommitOperationAdd(path_in_repo=str(p.relative_to(payload)),path_or_fileobj=str(p)) for p in files]
        commit=api.create_commit(repo_id=REPO,repo_type='model',revision='main',parent_commit=parent,
            operations=operations,commit_message='Add synchronized source videos and six clean ping-pong teasers')
        report=dict(revision=commit.oid,parent=parent,previous_page_revision=OLD_REVISION,
            new_files=sorted(actual),uploaded_bytes=sum(p.stat().st_size for p in files),
            local_sha256={str(p.relative_to(payload)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            existing_files_unchanged=False)
        atomic_json(report_path,report)
        current=inventory(api,commit.oid)
        if any(current.get(path)!=blob for path,blob in original.items()):
            raise ValueError('Previously pinned media changed unexpectedly; do not update the page pin')
        report['existing_files_unchanged']=True
        report['existing_files_verified']=len(original)
        atomic_json(report_path,report)
    if not report['existing_files_unchanged']:
        raise ValueError('Upload incomplete; inspect immutable-object verification')
    with ThreadPoolExecutor(max_workers=2) as executor:
        checks=list(executor.map(probe_url,[(path,report['revision']) for path in report['new_files']]))
    report['anonymous_checks']=checks
    report['status']='30anonymous checks passed; old pinned media unchanged'
    atomic_json(report_path,report)
    print(json.dumps({k:report[k] for k in ['revision','uploaded_bytes','existing_files_verified','status']},indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    publish(args.root)


if __name__=='__main__':
    main()

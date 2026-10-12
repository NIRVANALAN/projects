"""Freeze existing qualitative exports and paired metrics for the website.

No inference, alignment, or metric recomputation. Raw manifests remain intact.
"""
import argparse
import csv
import json
from pathlib import Path

from link_cowtracker_assets import collect_cases

LOG = Path('/scratch/shared/engs2907/logs/track4d-360')
SELECTED = LOG / 'project_page/selected_20261007'
RANKING = LOG / 'paper_assets_20261007_selected/native110_paired_ranking.tsv'


def title(value):
    return value.replace('_', ' ').replace('-', ' ').capitalize()


def robot_title(sequence):
    if sequence.startswith('figure_'):
        return 'Figure humanoid'
    if sequence.startswith('tesla_'):
        return 'Tesla humanoid'
    return 'DROID · '+sequence.split('__', 1)[0]


def camera_title(camera):
    if camera.startswith('vista4d_'):
        return 'Vista4D-inspired: '+title(camera.split('__')[-1])
    if 'safe_other_side' in camera:
        return 'Near-object '+('left' if 'left' in camera else 'right')+' orbit (60°)'
    return title(camera)


def selected_cases(kind, selected_root=SELECTED, fallback_root=None, refresh_cases=None):
    result = []
    paths = {path.parent.name: path for path in (fallback_root / kind).glob('*/manifest.json')} if fallback_root else {}
    paths.update({path.parent.name: path for path in (selected_root / kind).glob('*/manifest.json')
                  if not refresh_cases or f'{kind}/{path.parent.name}' in refresh_cases or path.parent.name not in paths})
    for path in sorted(paths.values(), key=lambda path: path.parent.name):
        manifest = json.loads(path.read_text())
        case = manifest['case']
        sequence = case['case_id']
        if kind in ('native110', 'davis', 'davis_cow'):
            scene, camera = sequence.split('__', 1)
        else:
            prediction = Path(case['prediction'])
            scene, camera = prediction.parent.parent.name, prediction.parent.name
        result.append(dict(
            id=f'filtered20261011_v2/{kind}/{sequence}' if 'v2' in manifest.get('presentation_filter', {}).get('policy', '') else f'filtered20261011/{kind}/{sequence}' if manifest.get('presentation_filter', {}).get('enabled') else f'{kind}/{sequence}', scene=robot_title(scene) if kind == 'robot' else title(scene), camera=camera_title(camera),
            clean=str(path.parent/'13_source_condition_synth_clean.mp4'),
            overlay=str(path.parent/'11_source_condition_synth_overlay.mp4'),
            source_manifest=str(path), backend=manifest['backend'],
            scene_id=('davis' if kind=='davis_cow' else kind)+'/'+scene, trajectory_id=camera,
            review_pending=kind=='davis_cow',
            note='Holo4D-14B (step 19,500) · '+manifest['backend'].replace('_', ' ')+(' · GMOS · 25 sampling steps' if kind=='davis_cow' else '')+(' · presentation-filtered tracks' if manifest.get('presentation_filter', {}).get('enabled') else ''),
            kind='blend', portrait_horizontal=kind == 'robot' and 'portrait' in case['comparison'],
        ))
    return result


def comparisons():
    # Include author-requested failures even without a metric win; no appearance claim.
    picks = [('snow-dog', 'crane-above'), ('fashion-walk', 'arc-left-right'),
             ('mountain-hike', 'truck-crane-below'), ('golf', 'dolly-out'),
             ('drive-desert', 'side-fly'), ('drive-desert', 'back-follow'),
             ('woman-beach', 'crane-above'), ('truck-pose', 'left-right'),
             ('friends-restaurant', 'side-dolly')]
    rows = {(r['video'], r['trajectory']): r for r in csv.DictReader(RANKING.open(), delimiter='\t')}
    result = []
    for scene, camera in picks:
        row = rows[(scene, camera)]
        numeric = {k: float(row[k]) for k in (
            'ours_pi3_rotation_error_deg', 'vista4d_pi3_rotation_error_deg',
            'ours_rot_err', 'vista4d_rot_err')}
        win = numeric['ours_pi3_rotation_error_deg'] < numeric['vista4d_pi3_rotation_error_deg'] and numeric['ours_rot_err'] < numeric['vista4d_rot_err']
        note = 'Matched trajectory comparison; per-video camera metrics are not appearance scores'
        if (scene, camera) == ('friends-restaurant', 'side-dolly'):
            note = 'Author-selected Vista4D face/orientation failure case; inspect the full video, not only the camera scores'
        result.append(dict(
            id=f'comparison/{scene}/{camera}', scene=title(scene), camera=title(camera),
            clean=row['ours_prediction'], baseline=row['vista4d_prediction'],
            source_manifest=str(RANKING), backend='vggt_omega_cowtracker',
            note=note,
            kind='comparison', metrics=numeric, metric_win_both=win,
        ))
    return result


def long_cases(picks_file=None):
    if picks_file:
        picks = json.loads(picks_file.read_text())
        result = []
        for pick in picks['approved']:
            root = Path(pick['root'])
            audit = json.loads((root/pick['audit']).read_text())
            if audit.get('failed', 0) or audit.get('failures'):
                raise ValueError('Long rollout protocol audit not cleared')
            passed = {(r['sequence'], r['trajectory']) for r in audit['records']}
            if (pick['source'], pick['trajectory']) not in passed:
                raise ValueError(f'Unaudited long candidate: {pick}')
            path = root/'long_rollout'/pick['source']/pick['trajectory']/'rollout_provenance.json'
            m = json.loads(path.read_text())
            result.append(dict(id=f"long_robot/{pick['source']}/{pick['trajectory']}",
                               scene=robot_title(pick['source']),camera=camera_title(pick['trajectory']),
                               clean=m['review_video'],source_manifest=str(path),kind='long',
                               note=f"{m['real_frames']} frames · {m['model_chunks']} chunks · T2V → I2V continuation",
                               chunks=m['model_chunks'],boundary_frames=list(range(49,m['real_frames'],48)),overlay_unavailable=True))
        return result
    root = LOG / 'benchmark/davis50_full_i2v_20261007'
    audit = json.loads((root/'rollout_validation.json').read_text())
    passed = {(r['sequence'], r['trajectory']) for r in audit['records']}
    picks = [('bear', 'pan_right'), ('classic-car', 'translate_right'),
             ('camel', 'orbit_left'), ('blackswan', 'pan_up'),
             ('lindy-hop', 'zoom_out'), ('koala', 'zoom_in')]
    result = []
    for scene, camera in picks:
        if (scene, camera) not in passed:
            raise ValueError(f'Unvalidated long rollout: {scene}/{camera}')
        path = root/'long_rollout'/scene/camera/'rollout_provenance.json'
        m = json.loads(path.read_text())
        result.append(dict(id=f'long/{scene}/{camera}', scene=title(scene), camera=title(camera),
                           clean=m['review_video'], source_manifest=str(path), kind='long',
                           note=f"{m['real_frames']} unique frames · {m['model_chunks']} chunks · T2V → I2V",
                           chunks=m['model_chunks'], boundary_frames=list(range(49, m['real_frames'], 48)),
                           overlay_unavailable=True))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--selected-root', type=Path, default=SELECTED)
    parser.add_argument('--fallback-root', type=Path, help='Reuse complete prior exports while newer cases finish; never publish fewer entries')
    parser.add_argument('--refresh-case', action='append', help='With fallback-root, replace only specified kind/case; always include newly added cases')
    parser.add_argument('--long-picks', type=Path)
    parser.add_argument('--expected-selected', type=int, default=0)
    args = parser.parse_args()
    archive = []
    excluded = []
    for c in collect_cases(True):
        item = dict(id='archive/'+str(Path(c['arm'])/c['sequence']/c['trajectory']),
                    scene=c['scene'], camera=c['camera'], clean=str(c['clean_src']),
                    overlay=str(c['overlay_src']), kind='blend', backend='4rc',
                    note=f"Archived {c['arm']} · 4RC geometry", source_manifest=str(c['clean_src'].parent/'manifest.json'))
        (excluded if c['status'] == 'known_content_failure' else archive).append(item)
    if args.refresh_case and not args.fallback_root:
        parser.error('--refresh-case requires --fallback-root')
    davis = [c for c in selected_cases('davis',args.selected_root) if c['scene'] != 'Classic car']
    davis += selected_cases('davis_cow',args.selected_root)
    sections = dict(robots=selected_cases('robot',args.selected_root,args.fallback_root,args.refresh_case), results=selected_cases('native110',args.selected_root,args.fallback_root,args.refresh_case),
                    comparisons=comparisons(), long=long_cases(args.long_picks), davis=davis)
    if args.expected_selected and len(sections['robots'])+len(sections['results']) != args.expected_selected:
        raise ValueError('Selected exports incomplete; refusing a partial page manifest')
    hero = next(c['id'] for c in sections['robots'] if c['camera'] == 'Subject orbit zoom' and c['scene'] == 'Figure humanoid')
    payload = dict(schema=1, hero=hero, sections=sections, excluded=excluded,
                   caveats=['Long-rollout protocol checks do not prove visual or motion quality; rejected candidates remain on disk.',
                            'Camera-metric wins are estimator-specific and do not certify appearance quality.',
                            'No continuous long-rollout track export exists here; long videos are clean source/generated pairs.',
                            'Presentation filtering changes display identities only; scientific RGB and conditioning caches are unchanged.'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2)+'\n')
    print({k: len(v) for k, v in sections.items()}, 'hero=', hero, flush=True)


if __name__ == '__main__':
    main()

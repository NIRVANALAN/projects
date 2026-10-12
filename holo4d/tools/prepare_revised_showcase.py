"""Reuse selections and add existing wall-safe robot outputs, no resampling."""
import argparse
import json
from pathlib import Path

LOG = Path('/scratch/shared/engs2907/logs/track4d-360')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--base-manifest', type=Path)
    p.add_argument('--include-davis', action='store_true')
    p.add_argument('--davis-only', action='store_true', help='Render only the existing paired DAVIS presentation assets')
    a = p.parse_args()
    plan = json.loads((a.base_manifest or LOG/'paper_assets_20261007_selected/review_manifest.json').read_text())
    cases = plan['cases']
    seen = {str(Path(c['prediction']).resolve()) for c in cases}
    root = LOG/'benchmark/robot_wall_safe_20260829/predictions'
    for dataset in sorted(root.iterdir()):
        for variant in sorted(dataset.iterdir()):
            for source in sorted(variant.iterdir()):
                # Extra restrained cameras; large/wall-crossing orbits remain
                # absent. These are review candidates, not automatic wins.
                for camera in ('slow_crane_dolly_in', 'slow_dolly_out', 'slow_dolly_in', 'slow_crane_down'):
                    pred = source/camera/'pred_rgb.mp4'
                    if pred.is_file() and str(pred.resolve()) not in seen:
                        if not (pred.parent/'source_condition.npz').is_file():
                            continue
                        seen.add(str(pred.resolve()))
                        cases.append(dict(kind='robot',case_id=f'extra_{source.name}__{camera}',
                                          prediction=str(pred), comparison=str(pred.parent/'comparison.mp4'), baseline=''))
    if a.include_davis:
        root = LOG/'benchmark/davis50_ab12_step19500_4rc_nogmos_50step_20261002/384x672/step-19500'
        # Each scene contributes two actual frozen trajectories. Classic car
        # uses the author-requested historical CoW/VGGT/GMOS arm, not 4RC.
        cases[:] = [c for c in cases if not (c['kind']=='davis' and c['case_id'].startswith('classic-car__'))]
        for scene in ('drift-turn','lindy-hop','bear'):
            for folder in sorted((root/scene).iterdir()):
                if not folder.is_dir() or not (folder/'pred_rgb.mp4').is_file():
                    continue
                camera = folder.name
                pred = folder/'pred_rgb.mp4'
                if not (pred.parent/'source_condition.npz').is_file():
                    raise FileNotFoundError(pred)
                if str(pred.resolve()) not in seen:
                    cases.append(dict(kind='davis', case_id=f'{scene}__{camera}', prediction=str(pred), comparison=str(pred.parent/'comparison.mp4'), baseline=''))
                    seen.add(str(pred.resolve()))
        cow = Path('/vgg/yushi/logs/holo4d/track4d-360/benchmark/civo_b200_davis50/ab12_384p_mild_step19500_cowvggt_gmos_staticdynfix/384x672/step-19500')
        for camera in ('translate_right','zoom_in'):
            pred = cow/'classic-car'/camera/'pred_rgb.mp4'
            if not pred.is_file():
                raise FileNotFoundError(pred)
            if str(pred.resolve()) not in seen:
                cases.append(dict(kind='davis_cow',case_id=f'classic-car__{camera}',prediction=str(pred),comparison=str(pred.parent/'comparison.mp4'),baseline='',sampling_steps=25))
                seen.add(str(pred.resolve()))
    cases.sort(key=lambda c: (0 if c['kind']=='davis_cow' else 1 if c['kind']=='davis' else 2 if 'breakdance' in c['case_id'] else 3 if c['kind']=='native110' else 4))
    if a.davis_only:
        plan['cases'] = [c for c in cases if c['kind'] in ('davis','davis_cow')]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan,indent=2)+'\n')
    print('[revised manifest]',len(cases),'robot',sum(c['kind']=='robot' for c in cases),flush=True)


if __name__ == '__main__':
    main()

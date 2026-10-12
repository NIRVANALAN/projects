#!/usr/bin/env python3
"""Symlink the CoWTracker V4 cherry-pick MP4s into the project page and emit the
slide manifest consumed by static/js/site.js.

Each case contributes two pixel-aligned composite videos of identical size and
duration:

  11_vista4d_style_source_condition_synth.mp4  -> overlay.mp4  (3D track overlay)
  13_source_condition_synth_clean.mp4          -> clean.mp4    (no overlay)

The page stacks the pair and cross-fades between them inside every carousel
slide, so the two files must stay frame-aligned. This script verifies that and
refuses to link a case whose pair disagrees on size, fps or frame count.

Nothing is copied: the linked MP4s live on scratch and are draft-only assets.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

SOURCE_ROOT = Path(
    "/scratch/shared/engs2907/logs/track4d-360/project_page/v4/cowtracker/vista4d_cherrypick"
)
PAGE_ROOT = Path(__file__).resolve().parent.parent
LINK_ROOT = PAGE_ROOT / "static" / "videos" / "cowtracker"
MANIFEST_JS = PAGE_ROOT / "static" / "js" / "examples.js"

ARMS = ("ab12_step19500", "dense_id_target_step22000")

CLEAN_SRC = "13_source_condition_synth_clean.mp4"
OVERLAY_SRC = "11_vista4d_style_source_condition_synth.mp4"
THUMB_SRC = "condition_first_rgb_track_explainer_cover.jpg"

# Curation status ordering: strongest cherry-picks first, known failures last.
STATUS_ORDER = {
    "better_than_vista4d": 0,
    "replace_ppt_demo": 1,
    "good": 2,
    "compare_to_baseline": 3,
    "check_vista4d_overlap": 4,
    "vista4d_overlap": 5,
    "known_content_failure": 9,
}


def prettify(slug: str) -> str:
    """`friends-restaurant` -> `Friends restaurant`."""
    words = slug.replace("_", " ").replace("-", " ").split()
    if not words:
        return slug
    return " ".join([words[0].capitalize()] + words[1:])


def iter_boxes(handle, start: int, end: int):
    """Yield ISO-BMFF child boxes as (type, payload_start, box_end)."""
    position = start
    while position + 8 <= end:
        handle.seek(position)
        header = handle.read(8)
        if len(header) != 8:
            break
        size, box_type = struct.unpack(">I4s", header)
        header_size = 8
        if size == 1:
            extended = handle.read(8)
            if len(extended) != 8:
                raise ValueError(f"truncated extended box header in {handle.name}")
            size = struct.unpack(">Q", extended)[0]
            header_size = 16
        elif size == 0:
            size = end - position
        if size < header_size or position + size > end:
            raise ValueError(f"invalid {box_type!r} box in {handle.name}")
        yield box_type, position + header_size, position + size
        position += size


def child_box(handle, parent: tuple[bytes, int, int], wanted: bytes):
    """Return one direct child box with the requested four-character code."""
    _, payload_start, box_end = parent
    return next((box for box in iter_boxes(handle, payload_start, box_end) if box[0] == wanted), None)


def read_exact(handle, offset: int, length: int) -> bytes:
    handle.seek(offset)
    data = handle.read(length)
    if len(data) != length:
        raise ValueError(f"truncated MP4 metadata in {handle.name}")
    return data


def probe(path: Path) -> dict:
    """Read video-track geometry and timing directly from ISO-BMFF boxes."""
    with path.open("rb") as handle:
        file_size = path.stat().st_size
        moov = next((box for box in iter_boxes(handle, 0, file_size) if box[0] == b"moov"), None)
        if moov is None:
            raise ValueError(f"missing moov box: {path}")

        for trak in (box for box in iter_boxes(handle, moov[1], moov[2]) if box[0] == b"trak"):
            tkhd = child_box(handle, trak, b"tkhd")
            mdia = child_box(handle, trak, b"mdia")
            if tkhd is None or mdia is None:
                continue
            hdlr = child_box(handle, mdia, b"hdlr")
            mdhd = child_box(handle, mdia, b"mdhd")
            minf = child_box(handle, mdia, b"minf")
            if hdlr is None or mdhd is None or minf is None:
                continue
            if read_exact(handle, hdlr[1] + 8, 4) != b"vide":
                continue
            stbl = child_box(handle, minf, b"stbl")
            stsz = child_box(handle, stbl, b"stsz") if stbl else None
            if stsz is None:
                raise ValueError(f"missing video sample table: {path}")

            tkhd_version = read_exact(handle, tkhd[1], 1)[0]
            dimension_offset = 88 if tkhd_version == 1 else 76
            width_fixed, height_fixed = struct.unpack(
                ">II", read_exact(handle, tkhd[1] + dimension_offset, 8)
            )
            width, height = width_fixed >> 16, height_fixed >> 16

            mdhd_version = read_exact(handle, mdhd[1], 1)[0]
            if mdhd_version == 1:
                timescale = struct.unpack(">I", read_exact(handle, mdhd[1] + 20, 4))[0]
                duration_ticks = struct.unpack(">Q", read_exact(handle, mdhd[1] + 24, 8))[0]
            else:
                timescale, duration_ticks = struct.unpack(
                    ">II", read_exact(handle, mdhd[1] + 12, 8)
                )
            frames = struct.unpack(">I", read_exact(handle, stsz[1] + 8, 4))[0]
            duration = duration_ticks / timescale
            return {
                "width": width,
                "height": height,
                "fps": frames / duration,
                "frames": frames,
                "duration": duration,
            }

    raise ValueError(f"missing video track: {path}")


def collect_cases(verify: bool) -> list[dict]:
    cases: list[dict] = []
    for arm in ARMS:
        arm_dir = SOURCE_ROOT / arm
        if not arm_dir.is_dir():
            raise SystemExit(f"missing arm directory: {arm_dir}")
        for case_dir in sorted(p for p in arm_dir.glob("*/*") if p.is_dir()):
            clean = case_dir / CLEAN_SRC
            overlay = case_dir / OVERLAY_SRC
            thumb = case_dir / THUMB_SRC
            manifest_path = case_dir / "manifest.json"
            missing = [p.name for p in (clean, overlay, thumb, manifest_path) if not p.is_file()]
            if missing:
                print(f"skip {arm}/{case_dir.parent.name}/{case_dir.name}: missing {missing}")
                continue

            manifest = json.loads(manifest_path.read_text())
            sequence, trajectory = case_dir.parent.name, case_dir.name

            if verify:
                clean_meta, overlay_meta = probe(clean), probe(overlay)
                for key in ("width", "height", "frames"):
                    if clean_meta[key] != overlay_meta[key]:
                        raise SystemExit(
                            f"{arm}/{sequence}/{trajectory}: clean/overlay disagree on {key} "
                            f"({clean_meta[key]} vs {overlay_meta[key]}); the cross-fade "
                            "requires a frame-aligned pair"
                        )
                for key in ("fps", "duration"):
                    if abs(clean_meta[key] - overlay_meta[key]) > 1e-6:
                        raise SystemExit(
                            f"{arm}/{sequence}/{trajectory}: clean/overlay disagree on {key} "
                            f"({clean_meta[key]} vs {overlay_meta[key]}); the cross-fade "
                            "requires a frame-aligned pair"
                        )
                geometry = clean_meta
            else:
                geometry = {
                    "width": int(manifest["width"]),
                    "height": int(manifest["height"]),
                    "fps": float(manifest["fps"]),
                    "frames": int(manifest["frames"]),
                    "duration": int(manifest["frames"]) / float(manifest["fps"]),
                }

            cases.append(
                {
                    "arm": arm,
                    "sequence": sequence,
                    "trajectory": trajectory,
                    "scene": prettify(sequence),
                    "camera": prettify(trajectory),
                    "status": manifest.get("curation_status", "unknown"),
                    "note": manifest.get("user_note", ""),
                    "clean_src": clean,
                    "overlay_src": overlay,
                    "thumb_src": thumb,
                    "geometry": geometry,
                }
            )
    return cases


def link_case(case: dict, dry_run: bool) -> str:
    """Create one case's clean, overlay, and thumbnail symlinks."""
    rel = Path(case["arm"]) / case["sequence"] / case["trajectory"]
    dest_dir = LINK_ROOT / rel
    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        for name, source in (("clean.mp4", case["clean_src"]), ("overlay.mp4", case["overlay_src"])):
            link = dest_dir / name
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(source)
        thumb_link = dest_dir / "thumb.jpg"
        if thumb_link.is_symlink() or thumb_link.exists():
            thumb_link.unlink()
        thumb_link.symlink_to(case["thumb_src"])
    return rel.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-pairs",
        action="store_true",
        help="decode each MP4 header to assert the clean/overlay pair is frame-aligned",
    )
    parser.add_argument("--dry-run", action="store_true", help="report without writing anything")
    args = parser.parse_args()

    cases = collect_cases(verify=args.verify_pairs)
    if not cases:
        raise SystemExit("no cases found")

    cases.sort(key=lambda c: (STATUS_ORDER.get(c["status"], 8), c["arm"], c["sequence"], c["trajectory"]))

    slides = []
    for case in cases:
        rel = link_case(case, args.dry_run)
        geometry = case["geometry"]
        slides.append(
            {
                "scene": case["scene"],
                "camera": case["camera"],
                "path": rel,
                "arm": case["arm"],
                "status": case["status"],
                "note": case["note"],
                "aspect": round(geometry["width"] / geometry["height"], 4),
                "duration": round(geometry["duration"], 4),
            }
        )

    payload = json.dumps(slides, indent=2)
    banner = (
        "// Generated by tools/link_cowtracker_assets.py — do not edit by hand.\n"
        f"// Source root: {SOURCE_ROOT}\n"
        "// Each entry maps to clean.mp4, overlay.mp4, and thumb.jpg under "
        "static/videos/cowtracker/<path>/.\n"
    )
    if args.dry_run:
        print(banner + f"// {len(slides)} slides (dry run, nothing written)")
    else:
        MANIFEST_JS.write_text(f"{banner}window.HOLO4D_EXAMPLES = {payload};\n")

    by_status: dict[str, int] = {}
    for slide in slides:
        by_status[slide["status"]] = by_status.get(slide["status"], 0) + 1
    print(f"{len(slides)} cases linked under {LINK_ROOT}")
    for status, count in sorted(by_status.items(), key=lambda kv: STATUS_ORDER.get(kv[0], 8)):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()

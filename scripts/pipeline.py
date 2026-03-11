#!/usr/bin/env python3
"""Evidence pipeline runner — orchestrate connectors and normalizers.

Runs source connectors (EPIC-001) to check for new content, normalizes
downloads (EPIC-002) into evidence pool markdown, and optionally stages
changes for git review.

Usage:
    python3 scripts/pipeline.py run                      # full pipeline
    python3 scripts/pipeline.py run --check-only         # dry run
    python3 scripts/pipeline.py run --connector vimeo    # single connector
    python3 scripts/pipeline.py run --stage              # stage changes in git

Discovery is always-on — connectors enumerate sources live on every run.
"""

import argparse
import glob
import logging
import os
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Evidence pool directory mapping:
#   connector type -> (pool directory name, source type for normalizer)
POOL_MAP = {
    "school-board-vtt": "school-board-budget-meetings",
    "city-council-vtt": "city-council-meetings-2026",
    "city-council-agenda": "city-council-meetings-2026",
    "budget-pdf": "fy27-budget-documents",
}

# Connector definitions: name, script path, data directories to watch
CONNECTORS = {
    "vimeo": {
        "script": os.path.join(SCRIPT_DIR, "connectors", "vimeo.py"),
        "watch_dirs": [
            os.path.join(PROJECT_ROOT, "data", "school-board", "meetings"),
            os.path.join(PROJECT_ROOT, "data", "city-council", "meetings"),
        ],
        "watch_pattern": "**/*.vtt",
    },
    "diligent": {
        "script": os.path.join(SCRIPT_DIR, "connectors", "diligent.py"),
        "watch_dirs": [
            os.path.join(PROJECT_ROOT, "data", "city-council", "meetings"),
        ],
        "watch_pattern": "**/agenda.txt",
    },
    "budget_page": {
        "script": os.path.join(SCRIPT_DIR, "connectors", "budget_page.py"),
        "watch_dirs": [
            os.path.join(PROJECT_ROOT, "data", "school-board", "budget-fy27", "documents"),
        ],
        "watch_pattern": "**/*",
    },
}


def snapshot_files(watch_dirs, pattern):
    """Return a set of all files matching pattern in watch directories."""
    files = set()
    for d in watch_dirs:
        if os.path.exists(d):
            for f in glob.glob(os.path.join(d, pattern), recursive=True):
                files.add(os.path.abspath(f))
    return files


def run_connector(name, check_only=False):
    """Run a connector script, return (exit_code, new_files).

    Snapshots the watch directories before and after to detect new files.
    """
    cfg = CONNECTORS[name]
    before = snapshot_files(cfg["watch_dirs"], cfg["watch_pattern"])

    cmd = [sys.executable, cfg["script"]]
    if check_only:
        cmd.append("--check-only")

    log.info("Running connector: %s", name)
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, timeout=300)
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        log.error("Connector %s timed out after 5 minutes", name)
        return 2, set()
    except Exception as e:
        log.error("Connector %s failed: %s", name, e)
        return 2, set()

    if check_only:
        return exit_code, set()

    after = snapshot_files(cfg["watch_dirs"], cfg["watch_pattern"])
    new_files = after - before
    if new_files:
        log.info("Connector %s produced %d new file(s)", name, len(new_files))
    else:
        log.info("Connector %s: no new files", name)
    return exit_code, new_files


def resolve_pool(filepath):
    """Determine which evidence pool a file belongs to based on its path."""
    rel = os.path.relpath(filepath, PROJECT_ROOT)

    if rel.startswith("data/school-board/meetings/") and filepath.endswith(".vtt"):
        return POOL_MAP["school-board-vtt"]
    elif rel.startswith("data/city-council/meetings/") and filepath.endswith(".vtt"):
        return POOL_MAP["city-council-vtt"]
    elif rel.startswith("data/city-council/meetings/") and filepath.endswith(".txt"):
        return POOL_MAP["city-council-agenda"]
    elif rel.startswith("data/school-board/budget-fy27/"):
        return POOL_MAP["budget-pdf"]
    return None


def infer_title(filepath):
    """Infer a reasonable title from the file path."""
    rel = os.path.relpath(filepath, PROJECT_ROOT)
    parts = rel.split(os.sep)

    # Extract date from path (look for YYYY-MM-DD patterns)
    date_part = ""
    for p in parts:
        if len(p) >= 10 and p[:4].isdigit() and p[4] == "-":
            date_part = p[:10]  # Take just YYYY-MM-DD
            break

    # Determine meeting type from path
    if "school-board" in rel:
        body = "School Board"
    elif "city-council" in rel:
        body = "City Council"
    else:
        body = "Meeting"

    if "budget-forum" in rel:
        kind = "Budget Forum"
    elif "budget-workshop" in rel:
        kind = "Budget Workshop"
    elif "workshop" in rel:
        kind = "Workshop"
    elif "regular" in rel:
        kind = "Regular Meeting"
    else:
        kind = "Meeting"

    if filepath.endswith(".vtt"):
        return f"{body} {kind} — {date_part}"
    elif filepath.endswith(".txt"):
        return f"{body} Agenda — {date_part}"
    elif filepath.endswith(".pdf") or filepath.endswith(".xlsx"):
        basename = os.path.splitext(os.path.basename(filepath))[0]
        return f"{basename.replace('-', ' ').replace('_', ' ').title()}"
    return os.path.basename(filepath)


def infer_date(filepath):
    """Extract a date string from the file path."""
    parts = filepath.split(os.sep)
    for p in parts:
        if len(p) >= 10 and p[:4].isdigit() and p[4] == "-":
            return p[:10]
    return None


def normalize_file(filepath):
    """Run the appropriate normalizer for a file. Returns True on success."""
    pool_name = resolve_pool(filepath)
    if not pool_name:
        log.warning("Cannot determine pool for %s — skipping normalization", filepath)
        return False

    pool_dir = os.path.join(PROJECT_ROOT, "docs", "evidence-pools", pool_name)
    if not os.path.exists(pool_dir):
        log.warning("Pool directory %s does not exist — skipping", pool_dir)
        return False

    title = infer_title(filepath)
    date = infer_date(filepath)

    if filepath.endswith(".vtt"):
        cmd = [sys.executable, "-m", "pipeline.normalize_vtt",
               filepath, pool_dir, "--title", title]
        if date:
            cmd.extend(["--date", date])
    elif filepath.endswith(".pdf"):
        cmd = [sys.executable, "-m", "pipeline.normalize_pdf",
               filepath, pool_dir, "--title", title]
        if date:
            cmd.extend(["--date", date])
    elif filepath.endswith(".xlsx"):
        cmd = [sys.executable, "-m", "pipeline.normalize_xlsx",
               filepath, pool_dir, "--title", title]
        if date:
            cmd.extend(["--date", date])
    elif filepath.endswith(".txt") or filepath.endswith(".html"):
        cmd = [sys.executable, "-m", "pipeline.normalize_html",
               filepath, pool_dir, "--title", title]
        if date:
            cmd.extend(["--date", date])
    else:
        log.warning("No normalizer for %s — skipping", filepath)
        return False

    log.info("Normalizing: %s → pool %s", os.path.basename(filepath), pool_name)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                cwd=PROJECT_ROOT, timeout=120)
        if result.returncode != 0:
            log.error("Normalizer failed for %s: %s", filepath,
                      result.stderr.strip() or result.stdout.strip())
            return False
        if result.stdout.strip():
            log.info("  %s", result.stdout.strip())
        return True
    except Exception as e:
        log.error("Normalizer error for %s: %s", filepath, e)
        return False


def stage_changes():
    """Stage all changes in data/ and docs/evidence-pools/ to the git index."""
    cmd = ["git", "add", "data/", "docs/evidence-pools/", "scripts/connectors/"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if result.returncode == 0:
        log.info("Changes staged in git index")
    else:
        log.warning("git add failed: %s", result.stderr.strip())


def collect_all_files(connector_names=None):
    """Collect all existing files from watch directories.

    Used by --normalize-all and the normalize subcommand to find files
    that may not have been normalized yet (e.g., downloaded outside
    the pipeline).
    """
    if connector_names is None:
        connector_names = list(CONNECTORS.keys())

    all_files = set()
    for name in connector_names:
        if name not in CONNECTORS:
            continue
        cfg = CONNECTORS[name]
        files = snapshot_files(cfg["watch_dirs"], cfg["watch_pattern"])
        all_files.update(files)

    # Also pick up XLSX files in budget-fy27 (not matched by *.pdf pattern)
    xlsx_dir = os.path.join(PROJECT_ROOT, "data", "school-board", "budget-fy27")
    if os.path.exists(xlsx_dir):
        for f in glob.glob(os.path.join(xlsx_dir, "**/*.xlsx"), recursive=True):
            all_files.add(os.path.abspath(f))

    return sorted(all_files)


def normalize_all(connector_names=None, stage=False):
    """Normalize all existing files, skipping those already in their pool.

    The normalizers handle deduplication via manifest hash checks,
    so it's safe to pass all files — duplicates are logged and skipped.
    """
    all_files = collect_all_files(connector_names)

    if not all_files:
        log.info("No files found to normalize")
        return 0

    stats = {"normalized": 0, "skipped_or_failed": 0}

    log.info("=" * 60)
    log.info("Normalizing all %d file(s) (duplicates will be skipped)", len(all_files))
    log.info("=" * 60)

    for filepath in all_files:
        if normalize_file(filepath):
            stats["normalized"] += 1
        else:
            stats["skipped_or_failed"] += 1

    if stage:
        log.info("")
        stage_changes()

    log.info("")
    log.info("=" * 60)
    log.info("Normalize-all complete: %d normalized, %d skipped/failed",
             stats["normalized"], stats["skipped_or_failed"])
    log.info("=" * 60)

    return 0


def run(connector_names=None, check_only=False, stage=False,
        normalize_all_flag=False):
    """Run the full pipeline."""
    if connector_names is None:
        connector_names = list(CONNECTORS.keys())

    stats = {
        "connectors_ok": 0,
        "connectors_failed": 0,
        "new_files": 0,
        "normalized": 0,
        "normalize_failed": 0,
    }

    all_new_files = []

    # Phase 1: Run connectors
    log.info("=" * 60)
    log.info("Phase 1: Running %d connector(s)%s",
             len(connector_names), " [CHECK ONLY]" if check_only else "")
    log.info("=" * 60)

    for name in connector_names:
        if name not in CONNECTORS:
            log.error("Unknown connector: %s (known: %s)",
                      name, ", ".join(CONNECTORS.keys()))
            stats["connectors_failed"] += 1
            continue

        exit_code, new_files = run_connector(name, check_only=check_only)
        if exit_code == 0:
            stats["connectors_ok"] += 1
        else:
            stats["connectors_failed"] += 1
            log.warning("Connector %s exited with code %d — continuing", name, exit_code)

        all_new_files.extend(sorted(new_files))

    stats["new_files"] = len(all_new_files)

    if check_only:
        log.info("=" * 60)
        log.info("Check complete: %d connector(s) checked, %d failed",
                 stats["connectors_ok"], stats["connectors_failed"])
        log.info("=" * 60)
        return 0 if stats["connectors_failed"] == 0 else 1

    # Phase 2: Normalize
    if normalize_all_flag:
        # Normalize ALL files in watch dirs (catches files downloaded outside pipeline)
        all_files = collect_all_files(connector_names)
        log.info("")
        log.info("=" * 60)
        log.info("Phase 2: Normalizing ALL %d file(s) (--normalize-all)", len(all_files))
        log.info("=" * 60)
        for filepath in all_files:
            if normalize_file(filepath):
                stats["normalized"] += 1
            else:
                stats["normalize_failed"] += 1
    elif all_new_files:
        log.info("")
        log.info("=" * 60)
        log.info("Phase 2: Normalizing %d new file(s)", len(all_new_files))
        log.info("=" * 60)
        for filepath in all_new_files:
            if normalize_file(filepath):
                stats["normalized"] += 1
            else:
                stats["normalize_failed"] += 1
    else:
        log.info("=" * 60)
        log.info("No new content — nothing to normalize")
        log.info("=" * 60)

    # Phase 3: Stage changes (optional)
    if stage:
        log.info("")
        log.info("=" * 60)
        log.info("Phase 3: Staging changes")
        log.info("=" * 60)
        stage_changes()

    # Summary
    log.info("")
    log.info("=" * 60)
    log.info("Pipeline complete")
    log.info("  Connectors: %d ok, %d failed",
             stats["connectors_ok"], stats["connectors_failed"])
    log.info("  New files: %d", stats["new_files"])
    log.info("  Normalized: %d ok, %d failed",
             stats["normalized"], stats["normalize_failed"])
    log.info("=" * 60)

    if stats["connectors_failed"] > 0 and stats["connectors_ok"] == 0:
        return 1  # total failure — all connectors failed
    return 0  # success or partial success


def main():
    parser = argparse.ArgumentParser(
        description="Evidence pipeline runner"
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run the pipeline")
    run_parser.add_argument(
        "--check-only", action="store_true",
        help="Dry run — show what would be fetched without downloading",
    )
    run_parser.add_argument(
        "--connector", action="append", dest="connectors",
        help="Run only specific connector(s) (can repeat)",
    )
    run_parser.add_argument(
        "--stage", action="store_true",
        help="Stage changes in git index after processing",
    )
    run_parser.add_argument(
        "--normalize-all", action="store_true",
        help="Normalize ALL files (not just new ones) — catches up un-pooled files",
    )

    # normalize subcommand: skip connectors, just normalize existing files
    norm_parser = subparsers.add_parser(
        "normalize", help="Normalize all existing data files into evidence pools",
    )
    norm_parser.add_argument(
        "--connector", action="append", dest="connectors",
        help="Only normalize files from specific connector watch dirs",
    )
    norm_parser.add_argument(
        "--stage", action="store_true",
        help="Stage changes in git index after processing",
    )

    args = parser.parse_args()

    if args.command == "run":
        exit_code = run(
            connector_names=args.connectors,
            check_only=args.check_only,
            stage=args.stage,
            normalize_all_flag=args.normalize_all,
        )
    elif args.command == "normalize":
        exit_code = normalize_all(
            connector_names=args.connectors,
            stage=args.stage,
        )
    else:
        parser.print_help()
        sys.exit(2)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

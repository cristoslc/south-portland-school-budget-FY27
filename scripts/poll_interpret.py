#!/usr/bin/env python3
"""Track 2 Polling Orchestrator — ADR-002.

Detects new/changed meeting bundles, runs the interpretation chain
(interpret → fold → brief) for affected meetings, and optionally
commits results.

This script is the local-machine counterpart to pipeline.yml (Track 1).
Track 1 runs on the runner and handles evidence collection + bundling.
Track 2 runs locally where Claude CLI is authenticated and handles
all LLM-dependent work.

Usage:
    python3 scripts/poll_interpret.py                # detect + process gaps
    python3 scripts/poll_interpret.py --dry-run      # show what would be done
    python3 scripts/poll_interpret.py --pull          # git pull before detecting
    python3 scripts/poll_interpret.py --brief 2026-03-19  # also generate briefs
    python3 scripts/poll_interpret.py --publish       # copy briefs to dist/

Exit codes:
    0 — success (or nothing to do)
    1 — one or more steps failed
    2 — usage error
"""

import argparse
import concurrent.futures
import datetime
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("poll_interpret")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

BUNDLES_DIR = PROJECT_ROOT / "data" / "interpretation" / "bundles"
MEETINGS_DIR = PROJECT_ROOT / "data" / "interpretation" / "meetings"
CUMULATIVE_DIR = PROJECT_ROOT / "data" / "interpretation" / "cumulative"
BRIEFS_DIR = PROJECT_ROOT / "data" / "interpretation" / "briefs"
DIST_BRIEFS_DIR = PROJECT_ROOT / "dist" / "enrollment-study" / "briefings"
PERSONA_DIR = PROJECT_ROOT / "docs" / "persona" / "Active"

MEETING_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(school-board|city-council)$")
PERSONA_DIR_RE = re.compile(r"^\(PERSONA-(\d{3})\)-.+$")


# ============================================================================
# Detection: what needs processing?
# ============================================================================

def count_personas():
    """Count validated personas."""
    if not PERSONA_DIR.exists():
        return 0
    return sum(
        1 for d in PERSONA_DIR.iterdir()
        if d.is_dir() and PERSONA_DIR_RE.match(d.name)
    )


def list_bundles():
    """Return sorted list of meeting IDs that have bundles."""
    if not BUNDLES_DIR.exists():
        return []
    return sorted(
        d.name for d in BUNDLES_DIR.iterdir()
        if d.is_dir() and MEETING_ID_RE.match(d.name)
        and (d / "manifest.yaml").exists()
    )


def list_persona_ids():
    """Return sorted list of validated persona IDs (e.g., ['PERSONA-001', ...])."""
    if not PERSONA_DIR.exists():
        return []
    ids = []
    for d in PERSONA_DIR.iterdir():
        m = PERSONA_DIR_RE.match(d.name)
        if d.is_dir() and m:
            ids.append(f"PERSONA-{m.group(1)}")
    return sorted(ids)


def existing_interpretations(meeting_id):
    """Return set of PERSONA-NNN IDs that already have interpretations."""
    meeting_dir = MEETINGS_DIR / meeting_id
    if not meeting_dir.exists():
        return set()
    return {
        f.stem
        for f in meeting_dir.iterdir()
        if f.is_file() and f.suffix == ".md"
        and re.match(r"^PERSONA-\d{3}$", f.stem)
    }


def count_interpretations(meeting_id):
    """Count PERSONA-NNN.md files in a meeting's interpretation dir."""
    return len(existing_interpretations(meeting_id))


def list_folded_meetings(persona_id):
    """Return set of meeting dates folded for a given persona."""
    persona_dir = CUMULATIVE_DIR / persona_id
    if not persona_dir.exists():
        return set()
    return {
        f.stem  # e.g., "2026-03-02"
        for f in persona_dir.iterdir()
        if f.is_file() and f.suffix == ".md" and f.name != "summary.md"
    }


def extract_meeting_date(meeting_id):
    """Extract the date portion from a meeting ID like '2026-03-02-school-board'."""
    parts = meeting_id.split("-")
    if len(parts) >= 3:
        return "-".join(parts[:3])
    return meeting_id


def detect_gaps(num_personas):
    """Detect all processing gaps across the pipeline.

    Only considers meetings on or before today (future meetings are
    bundled for scheduling but shouldn't be interpreted yet).

    Returns:
        dict with keys:
            needs_interpretation: list of meeting_ids needing interpretation
            needs_fold: list of meeting_ids needing folding (in chronological order)
            interpretation_complete: list of fully interpreted meeting_ids
    """
    bundles = list_bundles()
    today = datetime.date.today().isoformat()

    needs_interpretation = []
    interpretation_complete = []

    for meeting_id in bundles:
        # Skip future meetings
        meeting_date = extract_meeting_date(meeting_id)
        if meeting_date > today:
            continue

        count = count_interpretations(meeting_id)
        if count < num_personas:
            needs_interpretation.append((meeting_id, count))
        else:
            interpretation_complete.append(meeting_id)

    # Check fold gaps: meetings that are fully interpreted but not folded
    # Use PERSONA-001 as the reference (all personas should be in sync)
    folded = list_folded_meetings("PERSONA-001")
    needs_fold = []

    for meeting_id in interpretation_complete:
        meeting_date = extract_meeting_date(meeting_id)
        if meeting_date not in folded:
            needs_fold.append(meeting_id)

    # Also check meetings that were partially folded (some personas missing)
    # but only if they're fully interpreted
    if folded and interpretation_complete:
        # Check all personas for fold completeness on interpreted meetings
        all_persona_ids = sorted(
            f"PERSONA-{m.group(1)}"
            for d in PERSONA_DIR.iterdir()
            if d.is_dir() and (m := PERSONA_DIR_RE.match(d.name))
        )
        for meeting_id in interpretation_complete:
            meeting_date = extract_meeting_date(meeting_id)
            if meeting_date in folded and meeting_id not in needs_fold:
                # Check if ALL personas have this fold
                for pid in all_persona_ids:
                    pid_folded = list_folded_meetings(pid)
                    if meeting_date not in pid_folded:
                        needs_fold.append(meeting_id)
                        break

    # Sort needs_fold chronologically
    needs_fold.sort()

    return {
        "needs_interpretation": needs_interpretation,
        "needs_fold": needs_fold,
        "interpretation_complete": interpretation_complete,
    }


# ============================================================================
# Execution: run the pipeline steps
# ============================================================================

def run_script(script_name, args, description=""):
    """Run a pipeline script as a subprocess."""
    venv_python = str(PROJECT_ROOT / ".venv" / "bin" / "python3")
    if not os.path.isfile(venv_python):
        venv_python = "python3"
    cmd = [venv_python, str(SCRIPT_DIR / script_name)] + args
    log.info("  [exec] %s %s", script_name, " ".join(args))

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=600,  # 10 minutes per script call
        )
    except subprocess.TimeoutExpired:
        log.error("  [timeout] %s exceeded 10-minute limit", script_name)
        return False

    if result.returncode != 0:
        log.error("  [fail] %s exited %d", script_name, result.returncode)
        if result.stderr:
            for line in result.stderr.strip().splitlines()[-5:]:
                log.error("    %s", line)
        return False

    # Log last few info lines from stdout/stderr
    output = result.stderr or result.stdout
    if output:
        for line in output.strip().splitlines()[-3:]:
            log.info("    %s", line.strip())

    return True


def _run_parallel(tasks, max_workers):
    """Run a list of (script_name, args, description) tuples concurrently.

    Returns True if all succeeded, False if any failed.
    """
    if max_workers <= 1:
        # Serial fallback
        return all(run_script(s, a, d) for s, a, d in tasks)

    all_ok = True
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(run_script, script, args, desc): desc
            for script, args, desc in tasks
        }
        for future in concurrent.futures.as_completed(futures):
            desc = futures[future]
            try:
                if not future.result():
                    log.error("  [fail] %s", desc)
                    all_ok = False
            except Exception as exc:
                log.error("  [error] %s: %s", desc, exc)
                all_ok = False
    return all_ok


def run_interpretation(meeting_id, dry_run=False, max_workers=4):
    """Run interpret_meeting.py per persona in parallel, skipping completed."""
    all_personas = list_persona_ids()
    done = existing_interpretations(meeting_id)
    remaining = [p for p in all_personas if p not in done]

    if not remaining:
        log.info("  All personas already interpreted for %s", meeting_id)
        return True

    bundle_path = str(BUNDLES_DIR / meeting_id)
    tasks = []
    for persona_id in remaining:
        args = [bundle_path, "--persona", persona_id]
        if dry_run:
            args.append("--dry-run")
        tasks.append(("interpret_meeting.py", args,
                       f"Interpreting {meeting_id} {persona_id}"))

    log.info("  Dispatching %d persona(s) with %d workers", len(tasks), max_workers)
    return _run_parallel(tasks, max_workers)


def run_fold(meeting_id, dry_run=False, max_workers=4):
    """Run fold_meeting.py per persona in parallel (personas are independent)."""
    all_personas = list_persona_ids()
    tasks = []
    for persona_id in all_personas:
        args = [meeting_id, "--persona", persona_id]
        if dry_run:
            args.append("--dry-run")
        tasks.append(("fold_meeting.py", args,
                       f"Folding {meeting_id} {persona_id}"))

    log.info("  Dispatching %d persona(s) with %d workers", len(tasks), max_workers)
    return _run_parallel(tasks, max_workers)


def run_briefs(upcoming_date, dry_run=False, max_workers=4):
    """Run generate_briefs.py once for all persona and general briefs."""
    args = [upcoming_date, "--force"]
    if dry_run:
        args.append("--dry-run")
    return run_script("generate_briefs.py", args)


def publish_briefs(upcoming_date):
    """Copy generated persona and general briefs to dist/briefings/."""
    source_dir = BRIEFS_DIR / upcoming_date
    if not source_dir.exists():
        log.warning("No briefs found at %s", source_dir)
        return False

    DIST_BRIEFS_DIR.mkdir(parents=True, exist_ok=True)

    # Load persona name mapping
    persona_names = {}
    if PERSONA_DIR.exists():
        for subdir in PERSONA_DIR.iterdir():
            m = PERSONA_DIR_RE.match(subdir.name)
            if not m:
                continue
            persona_id = f"PERSONA-{m.group(1)}"
            # Extract slug from directory name
            slug = subdir.name.split(")-", 1)[-1] if ")-" in subdir.name else ""
            persona_names[persona_id] = slug.lower()

    count = 0
    for brief_file in sorted(source_dir.glob("PERSONA-*.md")):
        if brief_file.name == "PERSONA-000-upcoming.md":
            dest_name = "general-upcoming-briefing.md"
            dest_path = DIST_BRIEFS_DIR / dest_name
            shutil.copy2(brief_file, dest_path)
            count += 1
            log.info("  Published %s → %s", brief_file.name, dest_name)
            continue

        if brief_file.name == "PERSONA-000-evergreen.md":
            dest_name = "general-budget-briefing.md"
            dest_path = DIST_BRIEFS_DIR / dest_name
            shutil.copy2(brief_file, dest_path)
            count += 1
            log.info("  Published %s → %s", brief_file.name, dest_name)
            continue

        persona_id = brief_file.stem  # e.g., PERSONA-001
        slug = persona_names.get(persona_id, persona_id.lower())
        dest_name = f"{persona_id.lower().replace('persona-', 'persona-')}-{slug}.md"
        dest_path = DIST_BRIEFS_DIR / dest_name

        shutil.copy2(brief_file, dest_path)
        count += 1
        log.info("  Published %s → %s", brief_file.name, dest_name)

    # Clean up any raw PERSONA-*.md files in dist that weren't produced by
    # this publish step.  These appear when someone copies or commits pipeline
    # output directly instead of going through --publish.
    stale = 0
    for stray in sorted(DIST_BRIEFS_DIR.glob("PERSONA-*.md")):
        stray.unlink()
        stale += 1
        log.info("  Removed stale raw file %s", stray.name)
    if stale:
        log.info("Cleaned %d stale PERSONA-*.md file(s) from %s", stale, DIST_BRIEFS_DIR)

    log.info("Published %d brief(s) to %s", count, DIST_BRIEFS_DIR)
    return count > 0


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Track 2 Polling Orchestrator (ADR-002)"
    )
    parser.add_argument(
        "--pull", action="store_true",
        help="Run git pull before detecting gaps",
    )
    parser.add_argument(
        "--brief",
        metavar="DATE",
        help="Generate briefs for this upcoming meeting date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--publish", action="store_true",
        help="Copy generated briefs to dist/briefings/",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without making LLM calls",
    )
    parser.add_argument(
        "--skip-interpret", action="store_true",
        help="Skip interpretation step (only fold + brief)",
    )
    parser.add_argument(
        "--skip-fold", action="store_true",
        help="Skip fold step (only interpret + brief)",
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=4,
        help="Max concurrent LLM calls per step (default: 4)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    log.info("=== Track 2 Polling Orchestrator (ADR-002) ===")
    log.info("Date: %s", datetime.date.today().isoformat())
    log.info("Workers: %d", args.workers)

    if args.dry_run:
        log.info("Mode: DRY RUN")

    # Optional: pull latest
    if args.pull:
        log.info("")
        log.info("--- Pulling latest ---")
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            log.error("git pull failed: %s", result.stderr.strip())
            sys.exit(2)
        log.info("  %s", result.stdout.strip())

    # Detect gaps
    log.info("")
    log.info("--- Detecting gaps ---")
    num_personas = count_personas()
    log.info("Validated personas: %d", num_personas)

    if num_personas == 0:
        log.error("No personas found in %s", PERSONA_DIR)
        sys.exit(2)

    gaps = detect_gaps(num_personas)
    total_bundles = len(list_bundles())

    log.info("Bundles: %d total", total_bundles)
    log.info("Needs interpretation: %d meeting(s)", len(gaps["needs_interpretation"]))
    for mid, count in gaps["needs_interpretation"]:
        log.info("  %s (%d/%d personas)", mid, count, num_personas)
    log.info("Needs fold: %d meeting(s)", len(gaps["needs_fold"]))
    for mid in gaps["needs_fold"]:
        log.info("  %s", mid)

    had_failures = False

    # Step 1: Interpret missing meetings
    if not args.skip_interpret and gaps["needs_interpretation"]:
        log.info("")
        log.info("--- Step 1: Interpretation ---")
        for meeting_id, existing_count in gaps["needs_interpretation"]:
            log.info("[%s] %d/%d personas done, running remaining...",
                     meeting_id, existing_count, num_personas)
            ok = run_interpretation(meeting_id, dry_run=args.dry_run, max_workers=args.workers)
            if not ok:
                log.error("[%s] Interpretation failed — continuing", meeting_id)
                had_failures = True
            else:
                # After successful interpretation, this meeting may need folding
                if meeting_id not in gaps["needs_fold"]:
                    # Verify it's now complete
                    new_count = count_interpretations(meeting_id)
                    if new_count >= num_personas:
                        gaps["needs_fold"].append(meeting_id)
                        gaps["needs_fold"].sort()
    elif not args.skip_interpret:
        log.info("")
        log.info("--- Step 1: Interpretation — nothing to do ---")

    # Step 2: Fold meetings (must be chronological)
    if not args.skip_fold and gaps["needs_fold"]:
        log.info("")
        log.info("--- Step 2: Cumulative Fold ---")
        log.info("Processing %d meeting(s) in chronological order",
                 len(gaps["needs_fold"]))
        for meeting_id in gaps["needs_fold"]:
            log.info("[%s] Folding...", meeting_id)
            ok = run_fold(meeting_id, dry_run=args.dry_run, max_workers=args.workers)
            if not ok:
                log.error("[%s] Fold failed — stopping fold chain "
                          "(subsequent folds depend on this)", meeting_id)
                had_failures = True
                break
    elif not args.skip_fold:
        log.info("")
        log.info("--- Step 2: Cumulative Fold — nothing to do ---")

    # Step 3: Generate briefs
    if args.brief:
        log.info("")
        log.info("--- Step 3: Brief Generation ---")
        try:
            datetime.date.fromisoformat(args.brief)
        except ValueError:
            log.error("Invalid date: %s", args.brief)
            sys.exit(2)

        ok = run_briefs(args.brief, dry_run=args.dry_run, max_workers=args.workers)
        if not ok:
            had_failures = True

        # Step 4: Publish
        if args.publish and ok and not args.dry_run:
            log.info("")
            log.info("--- Step 4: Publishing ---")
            publish_briefs(args.brief)

    # Summary
    log.info("")
    log.info("=== Done ===")
    if had_failures:
        log.warning("Some steps failed — check output above")
        sys.exit(1)
    else:
        log.info("All steps completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()

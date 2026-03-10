#!/usr/bin/env python3
"""Parse a VTT transcript file and output merged markdown transcript text.

Usage: python3 parse_vtt.py <vtt_file>

Outputs to stdout:
  - Line 1: duration in HH:MM:SS format
  - Remaining lines: merged transcript with **[MM:SS]** timestamps every ~30-60 seconds
"""

import sys
import re


def parse_timestamp(ts_str):
    """Parse HH:MM:SS.mmm or MM:SS.mmm to total seconds."""
    parts = ts_str.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return 0.0


def format_mmss(seconds):
    """Format seconds as MM:SS."""
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def format_hhmmss(seconds):
    """Format seconds as HH:MM:SS."""
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_vtt(filepath):
    """Parse VTT file, return list of (start_seconds, text) segments."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into blocks separated by blank lines
    blocks = re.split(r"\n\n+", content)
    segments = []

    for block in blocks:
        lines = block.strip().split("\n")
        # Find the timestamp line
        ts_line = None
        text_lines = []
        for line in lines:
            if "-->" in line:
                ts_line = line
            elif ts_line is not None:
                # Lines after timestamp are text
                text_lines.append(line.strip())

        if ts_line and text_lines:
            # Parse start time
            start_str = ts_line.split("-->")[0].strip()
            start_sec = parse_timestamp(start_str)
            end_str = ts_line.split("-->")[1].strip()
            end_sec = parse_timestamp(end_str)
            text = " ".join(text_lines)
            segments.append((start_sec, end_sec, text))

    return segments


def merge_segments(segments, group_interval=45):
    """Merge segments into groups of ~group_interval seconds."""
    if not segments:
        return [], 0

    groups = []
    current_start = segments[0][0]
    current_texts = []
    last_end = 0

    for start, end, text in segments:
        last_end = end
        if current_texts and (start - current_start) >= group_interval:
            groups.append((current_start, " ".join(current_texts)))
            current_start = start
            current_texts = [text]
        else:
            current_texts.append(text)

    if current_texts:
        groups.append((current_start, " ".join(current_texts)))

    return groups, last_end


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_vtt.py <vtt_file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    segments = parse_vtt(filepath)

    if not segments:
        print("00:00:00")
        print("(No transcript content found)")
        return

    groups, duration_sec = merge_segments(segments)

    # Print duration as first line
    print(format_hhmmss(duration_sec))

    # Print merged transcript
    for start, text in groups:
        print(f"\n**[{format_mmss(start)}]** {text}")


if __name__ == "__main__":
    main()

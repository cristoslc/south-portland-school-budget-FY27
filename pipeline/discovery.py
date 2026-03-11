"""Discovery history for live-discovery connectors.

Provides DiscoveryHistory: a JSONL-backed store for tracking discovered URLs,
download attempt results, and exponential backoff for failures.

Each connector writes to data/<connector>/discovery.jsonl. Each line is a
complete snapshot of a URL's state at the time of an update:

    {"url": "...", "label": "...", "first_seen": "...", "last_attempt": "...",
     "status": "ok|failed|skipped", "fail_count": N, "last_error": "..."}

Backoff formula: skip URL if last_attempt + min(2^fail_count, 48) hours > now.
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone

log = logging.getLogger(__name__)


class DiscoveryHistory:
    """JSONL-backed history of discovered URLs and download attempts.

    Args:
        jsonl_path: Absolute path to the discovery.jsonl file.
    """

    def __init__(self, jsonl_path):
        self.path = jsonl_path
        self._records = {}  # url -> latest record dict
        self._load()

    def _load(self):
        """Load all records from the JSONL file; last entry per URL wins."""
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    self._records[record["url"]] = record
                except (json.JSONDecodeError, KeyError) as e:
                    log.warning("discovery.jsonl line %d invalid, skipping: %s", lineno, e)

    def should_attempt(self, url):
        """Return True if the URL should be attempted now.

        Returns False (skip) if the URL is within its backoff window:
            last_attempt + min(2^fail_count, 48) hours > now

        A URL with status 'ok' or no history is always attempted.
        """
        record = self._records.get(url)
        if record is None:
            return True
        if record.get("status") == "ok":
            return True

        fail_count = record.get("fail_count", 0)
        last_attempt_str = record.get("last_attempt")
        if not last_attempt_str:
            return True

        backoff_hours = min(2 ** fail_count, 48)
        try:
            last_attempt = datetime.fromisoformat(last_attempt_str.replace("Z", "+00:00"))
        except ValueError:
            log.warning("Cannot parse last_attempt '%s' for %s — will attempt", last_attempt_str, url)
            return True

        next_attempt = last_attempt + timedelta(hours=backoff_hours)
        if datetime.now(timezone.utc) < next_attempt:
            log.debug(
                "Skipping %s — backoff active (fail_count=%d, next attempt at %s)",
                url, fail_count, next_attempt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            return False
        return True

    def record_attempt(self, url, label, status, error=None):
        """Record a download attempt for a URL.

        Args:
            url: The URL that was attempted.
            label: Human-readable label (title, filename, etc.).
            status: One of 'ok', 'failed', 'skipped'.
            error: Optional error message string (for failed attempts).
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if url in self._records:
            record = dict(self._records[url])
        else:
            record = {
                "url": url,
                "label": label or "",
                "first_seen": now,
                "last_attempt": now,
                "status": status,
                "fail_count": 0,
                "last_error": None,
            }

        record["last_attempt"] = now
        record["status"] = status
        if label:
            record["label"] = label

        if status == "ok":
            record["fail_count"] = 0
            record["last_error"] = None
        elif status == "failed":
            record["fail_count"] = record.get("fail_count", 0) + 1
            record["last_error"] = error
        # 'skipped' leaves fail_count and last_error unchanged

        self._records[url] = record
        self._append(record)

    def _append(self, record):
        """Append a record snapshot to the JSONL file."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def discovered_urls(self):
        """Return a list of all known URL record dicts.

        Each dict has keys: url, label, first_seen, last_attempt, status,
        fail_count, last_error.
        """
        return list(self._records.values())

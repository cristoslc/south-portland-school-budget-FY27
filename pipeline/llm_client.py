"""Shared LLM client using opencode run --attach (ollama-cloud/deepseek-v4-pro:cloud high).

Uses opencode as the LLM backend, connected to the local opencode server.
Never touches claude -p or Anthropic API credits.
"""

import json
import logging
import os
import subprocess
import sys

ENCODING = "utf-8"

log = logging.getLogger(__name__)

DEFAULT_MODEL = "ollama-cloud/deepseek-v4-pro:cloud"
DEFAULT_VARIANT = "high"

OPENCODE_BIN = "/opt/homebrew/bin/opencode"
OPENCODE_SERVER = os.environ.get("OPENCODE_SERVER", "http://localhost:4096")
OPENCODE_PASSWORD = os.environ.get("OPENCODE_SERVER_PASSWORD", "Btjms3141")


def call_llm(
    prompt: str, *, system_prompt: str = "", model: str = DEFAULT_MODEL
) -> str:
    """Call opencode via `opencode run --attach` and return the text response.

    Prompts are passed via stdin to avoid shell argument length limits.
    If a system_prompt is provided, it is embedded in the prompt as a
    <system> ... </system> block since opencode has no --system-prompt flag.

    Args:
        prompt: The user prompt.
        system_prompt: Optional system instructions (embedded in prompt).
        model: Model ID in provider/model format (default: ollama-cloud/deepseek-v4-pro:cloud).

    Returns:
        The model's text response as a string.

    Raises:
        subprocess.CalledProcessError: If the CLI exits with a non-zero code.
        ValueError: If the response JSON stream contains no text content.
        FileNotFoundError: If the opencode binary is not found.
    """
    if system_prompt:
        full_prompt = f"<system>\n{system_prompt}\n</system>\n\n{prompt}"
    else:
        full_prompt = prompt

    cmd = [
        OPENCODE_BIN,
        "run",
        "--attach",
        OPENCODE_SERVER,
        "--model",
        model,
        "--variant",
        DEFAULT_VARIANT,
        "--format",
        "json",
        "--password",
        OPENCODE_PASSWORD,
    ]

    log.debug("Calling opencode: model=%s, prompt_len=%d", model, len(full_prompt))

    result = subprocess.run(
        cmd,
        input=full_prompt,
        capture_output=True,
        text=True,
        check=True,
        env={k: v for k, v in os.environ.items()},
    )

    text_parts = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            log.debug("Skipping non-JSON line: %s", line[:80])
            continue
        if event.get("type") == "text":
            part = event.get("part", {})
            txt = part.get("text", "")
            if txt:
                text_parts.append(txt)
        elif event.get("type") == "result" and event.get("is_error"):
            err_text = event.get("result", "")[:200]
            raise ValueError(f"opencode returned error: {err_text}")

    if not text_parts:
        log.error("opencode stdout dump: %s", result.stdout[:2000])
        raise ValueError("opencode response contained no text content")

    return "".join(text_parts)

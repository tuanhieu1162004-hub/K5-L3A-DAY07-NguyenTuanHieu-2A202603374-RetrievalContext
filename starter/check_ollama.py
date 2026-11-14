"""Check a real local Ollama model before connecting the Day 7 agent.

Uses only stdlib. Does not install/download models or run any benchmark cases.
The optional chat sends only a tiny connectivity prompt, no corpus or gold.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import socket
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:11434"


def request_json(path, payload=None, *, timeout=5):
    request = Request(BASE_URL + path, data=None if payload is None else json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json"})
    # Keep local health checks local even when the system has a web proxy.
    opener = build_opener(ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"Ollama HTTP {error.code} for {path}. Check that the model is installed and Ollama is up to date.") from None
    except (URLError, OSError, socket.timeout):
        raise RuntimeError("Cannot reach local Ollama or the request timed out. Open Ollama and retry.") from None
    except (ValueError, UnicodeError):
        raise RuntimeError("Ollama returned an invalid JSON response.") from None


def thinking_setting(details):
    """Respect the values actually advertised by this installed model."""
    thinking = details.get("thinking") or {}
    values = thinking.get("values", [])
    if any(value is False for value in values):
        return False
    if any(value is True for value in values):
        return True
    return thinking.get("default")


def require_complete(response):
    if not response.get("done") or response.get("done_reason") == "length":
        raise RuntimeError("Model output was incomplete or hit the token limit; increase num_predict and retry on dev.")
    message = response.get("message")
    if not isinstance(message, dict):
        raise RuntimeError("Model response has no valid message.")
    return message


def check(model, *, chat=False, timeout=180):
    report = {"status": "checking", "model": model, "base_url": BASE_URL,
              "checked_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds"),
              "benchmark_run": False, "tool_calling_exercised": False}
    try:
        report["ollama_version"] = request_json("/api/version")["version"]
        tags = request_json("/api/tags").get("models", [])
        installed = next((row for row in tags if model in (row.get("name"), row.get("model"))), None)
        if installed is None:
            raise RuntimeError(f"Model not installed. Run: ollama pull {model}")
        details = request_json("/api/show", {"model": model})
        if installed.get("remote_host") or details.get("remote_host") or details.get("remote_model"):
            raise RuntimeError("This check is for a local model. Select the downloaded qwen3:4b model.")
        capabilities = details.get("capabilities", [])
        report.update(model_digest=installed.get("digest"), model_size_bytes=installed.get("size"),
                      model_details=details.get("details", {}), capabilities=capabilities,
                      thinking=thinking_setting(details),
                      tool_calling_advertised="tools" in capabilities,
                      chat_tested=False)
        if "tools" not in capabilities:
            raise RuntimeError("Model does not advertise tool calling; choose qwen3:4b or another tools-capable local model.")
        if chat:
            print("Loading local model and checking a short chat response...", file=sys.stderr, flush=True)
            started = time.perf_counter()
            response = request_json("/api/chat", {
                "model": model, "stream": False, "think": thinking_setting(details),
                "messages": [{"role": "user", "content": "Reply with exactly OK and nothing else."}],
                "options": {"temperature": 0, "seed": 42, "num_ctx": 4096, "num_predict": 256},
                "keep_alive": "5m",
            }, timeout=timeout)
            message = require_complete(response)
            content = message.get("content", "")
            report.update(chat_response=content, done_reason=response.get("done_reason"),
                          thinking_characters=len(message.get("thinking", "")))
            if not isinstance(content, str) or content.strip() != "OK":
                raise RuntimeError("The connectivity prompt did not return the complete expected OK response.")
            report.update(chat_tested=True, elapsed_seconds=time.perf_counter()-started,
                          prompt_tokens=response.get("prompt_eval_count"), output_tokens=response.get("eval_count"),
                          ollama_total_duration_ns=response.get("total_duration"))
        report["status"] = "ready"
        report["note"] = "Connectivity/model capability check only. Native tool calling, citation support and abstention are evaluated separately in agent runs."
    except (RuntimeError, KeyError, TypeError) as error:
        report.update(status="error", error=str(error))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--chat", action="store_true", help="Also send one tiny prompt to the real local model")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", type=Path, default=ROOT / "starter/results/ollama-check.json")
    args = parser.parse_args()
    if not args.model.strip() or args.model.endswith(":cloud") or args.timeout < 1:
        parser.error("Choose a nonempty local model name and a positive timeout")
    report = check(args.model, chat=args.chat, timeout=args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "ready":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

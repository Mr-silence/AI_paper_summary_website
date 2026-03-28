import json
import sys
import time
from pathlib import Path

from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, OpenAI, PermissionDeniedError, RateLimitError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings


def _build_client() -> OpenAI:
    api_key = settings.LLM_API_KEY
    if not api_key:
        raise RuntimeError("No LLM API key configured. Set MINIMAX_API_KEY (or legacy KIMI_API_KEY).")

    return OpenAI(
        api_key=api_key,
        base_url=settings.KIMI_BASE_URL,
        timeout=settings.KIMI_TIMEOUT_SECONDS,
        max_retries=0,
    )


def _create_completion(client: OpenAI, **kwargs):
    max_retries = max(1, int(settings.KIMI_MAX_RETRIES or 1))
    last_error = None
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except (AuthenticationError, PermissionDeniedError) as exc:
            raise RuntimeError("Kimi authentication failed. Check KIMI_API_KEY permissions and validity.") from exc
        except RateLimitError as exc:
            last_error = exc
            if attempt >= max_retries - 1:
                raise RuntimeError("Kimi rate limit exceeded during connectivity checks.") from exc
            wait_seconds = min(15 * (attempt + 1), 60)
            print(f"[check_kimi] rate limited, retrying in {wait_seconds}s", flush=True)
            time.sleep(wait_seconds)
        except (APIConnectionError, APITimeoutError) as exc:
            last_error = exc
            if attempt >= max_retries - 1:
                raise RuntimeError("Kimi connectivity check timed out after retries.") from exc
            print(f"[check_kimi] connection timed out on attempt {attempt + 1}, retrying", flush=True)
            time.sleep(min(2 ** attempt, 4))
        except APIError as exc:
            last_error = exc
            if attempt >= max_retries - 1:
                raise RuntimeError(f"Kimi connectivity check failed after retries: {exc}") from exc
            print(f"[check_kimi] API error on attempt {attempt + 1}, retrying", flush=True)
            time.sleep(min(2 ** attempt, 4))

    raise RuntimeError("Kimi connectivity check failed without a recoverable response.") from last_error


def run_checks() -> dict[str, object]:
    client = _build_client()

    chat_completion = _create_completion(
        client,
        model=settings.KIMI_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Reply with exactly: pong"},
        ],
    )
    chat_content = (chat_completion.choices[0].message.content or "").strip()
    if not chat_content:
        raise RuntimeError("Kimi plain-text check returned empty content.")

    json_completion = _create_completion(
        client,
        model=settings.KIMI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return a JSON object with exactly two fields: "
                    '{"status":"ok","lang":"zh"}'
                ),
            },
            {"role": "user", "content": "Generate the JSON object now."},
        ],
        response_format={"type": "json_object"},
    )
    json_content = json_completion.choices[0].message.content or ""
    parsed_json = json.loads(json_content)
    if not isinstance(parsed_json, dict):
        raise RuntimeError("Kimi JSON Mode check did not return a JSON object.")

    return {
        "kimi_ready": True,
        "model": settings.KIMI_MODEL,
        "plain_text_sample": chat_content,
        "json_mode_sample": parsed_json,
    }


def main() -> None:
    result = run_checks()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

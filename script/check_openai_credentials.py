#!/usr/bin/env python3
"""
check_openai_credentials.py

Simple script to verify OpenAI API credentials by calling the models list endpoint.
Usage:
  # using environment variable
  OPENAI_API_KEY="sk-..." python script/check_openai_credentials.py

  # or pass key and base explicitly
  python script/check_openai_credentials.py --key sk-... --base https://api.openai.com
"""
from __future__ import annotations
import os
import sys
import argparse
import requests


def parse_args():
    p = argparse.ArgumentParser(description="Check OpenAI API key validity by listing models and testing a query.")
    p.add_argument("--key", "-k", help="OpenAI API key. If omitted, reads OPENAI_API_KEY env var.")
    p.add_argument(
        "--base",
        "-b",
        default=os.environ.get("OPENAI_API_BASE", "https://api.openai.com"),
        help="API base URL (default: https://api.openai.com or OPENAI_API_BASE env var).",
    )
    p.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds.")
    p.add_argument("--skip-query", action="store_true", help="Skip the simple query test.")
    return p.parse_args()


def test_simple_query(key: str, base: str, timeout: float = 10.0) -> bool:
    """
    Test a simple chat completion query to verify the API is working.
    Returns True if successful, False otherwise.
    """
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    url = base.rstrip("/") + "/v1/chat/completions"
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Say 'Hello' in one word"}
        ],
        "max_tokens": 10
    }
    
    print("\n" + "="*60)
    print("Testing simple query: 'Say Hello in one word'")
    print("="*60)
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        print(f"ERROR: Query test failed - Network error: {exc}", file=sys.stderr)
        return False
    
    if r.status_code == 200:
        try:
            data = r.json()
            if "choices" in data and len(data["choices"]) > 0:
                response = data["choices"][0]["message"]["content"]
                print(f"✓ Query test PASSED")
                print(f"  Model: {data.get('model', 'unknown')}")
                print(f"  Response: {response}")
                print(f"  Tokens used: {data.get('usage', {}).get('total_tokens', 'unknown')}")
                return True
            else:
                print("WARNING: Query returned 200 but unexpected format", file=sys.stderr)
                print(f"Response: {data}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"ERROR: Failed to parse query response: {e}", file=sys.stderr)
            print(f"Raw response: {r.text}", file=sys.stderr)
            return False
    else:
        print(f"✗ Query test FAILED: status {r.status_code}", file=sys.stderr)
        try:
            print(f"Response: {r.json()}", file=sys.stderr)
        except Exception:
            print(f"Response (text): {r.text}", file=sys.stderr)
        return False


def check_key(key: str, base: str, timeout: float = 10.0) -> int:
    """
    Returns exit code:
      0 - success (valid key)
      2 - authentication error (invalid/unauthorized)
      1 - other error (network / unexpected)
    """
    headers = {"Authorization": f"Bearer {key}"}
    # Prefer OpenAI-compatible endpoint /v1/models
    url = base.rstrip("/") + "/v1/models"
    
    print("="*60)
    print("Step 1: Checking API authentication")
    print("="*60)
    
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        print(f"ERROR: Network request failed: {exc}", file=sys.stderr)
        return 1

    if r.status_code == 200:
        try:
            data = r.json()
        except Exception:
            print("OK — received 200 but failed to parse JSON. Raw response below:\n")
            print(r.text)
            return 0
        # Try to print a concise success summary
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            print(f"✓ Authentication SUCCESS")
            print(f"  Models available: {len(data['data'])}")
            # print up to 10 model ids
            print("  Sample models:")
            for m in data["data"][:10]:
                mid = m.get("id") if isinstance(m, dict) else str(m)
                print(f"    - {mid}")
            return 0
        # OpenAI sometimes returns list directly
        if isinstance(data, list):
            print(f"✓ Authentication SUCCESS")
            print(f"  Models available: {len(data)}")
            print("  Sample models:")
            for m in data[:10]:
                mid = m.get("id") if isinstance(m, dict) else str(m)
                print(f"    - {mid}")
            return 0
        # Fallback
        print("✓ Authentication SUCCESS")
        print("Response:")
        print(data)
        return 0
    elif r.status_code in (401, 403):
        print(f"✗ AUTH ERROR: status {r.status_code}. Key is invalid or unauthorized.", file=sys.stderr)
        try:
            print("Response:", r.json(), file=sys.stderr)
        except Exception:
            print("Response (text):", r.text, file=sys.stderr)
        return 2
    else:
        print(f"✗ ERROR: unexpected status {r.status_code}", file=sys.stderr)
        try:
            print("Response:", r.json(), file=sys.stderr)
        except Exception:
            print("Response (text):", r.text, file=sys.stderr)
        return 1


def main():
    args = parse_args()

    key = args.key or os.environ.get("OPENAI_API_KEY")
    if not key:
        print("ERROR: No API key provided. Use --key or set OPENAI_API_KEY environment variable.", file=sys.stderr)
        return 1

    print("\n" + "="*60)
    print("OpenAI API Credentials Check")
    print("="*60 + "\n")

    # Step 1: Check authentication
    code = check_key(key, args.base, timeout=args.timeout)
    
    if code != 0:
        return code
    
    # Step 2: Test simple query (unless skipped)
    if not args.skip_query:
        query_success = test_simple_query(key, args.base, timeout=args.timeout)
        if not query_success:
            print("\n" + "="*60)
            print("SUMMARY: Authentication passed but query test failed")
            print("="*60)
            return 1
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED - API is fully functional")
    print("="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())


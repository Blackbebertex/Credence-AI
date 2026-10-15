#!/usr/bin/env python3
"""
CredenceAI-Gov Render Free Tier Keep-Alive Pinger.

Pings the backend `/health` endpoint periodically (e.g. every 10 minutes)
to prevent Render free tier instances from spinning down after 15 minutes of inactivity.
"""

import argparse
import datetime
import sys
import time
import urllib.error
import urllib.request


def ping(url: str, timeout: int = 30) -> bool:
    """Send an HTTP GET request to the target URL."""
    health_url = url.rstrip("/")
    if not health_url.endswith("/health"):
        health_url += "/health"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    req = urllib.request.Request(
        health_url,
        headers={"User-Agent": "CredenceGov-KeepAlive/1.0"},
    )

    try:
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.time() - start_time) * 1000
            status_code = response.getcode()
            print(f"[{timestamp}] SUCCESS -> {health_url} (status: {status_code}, latency: {latency:.1f}ms)")
            return True
    except urllib.error.HTTPError as exc:
        print(f"[{timestamp}] HTTP ERROR -> {health_url} (status: {exc.code})")
        return False
    except Exception as exc:
        print(f"[{timestamp}] CONNECTION FAILED -> {health_url} ({exc})")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Keep Render Free Tier backend awake")
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="Backend base URL or health URL (e.g., https://credence-gov-backend.onrender.com)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=600,
        help="Ping interval in seconds (default: 600s = 10 minutes, must be < 900s)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Ping once and exit immediately (useful for cron jobs and CI/CD)",
    )

    args = parser.parse_args()

    if args.interval >= 900:
        print("Warning: Render free tier spins down after 15 minutes (900s). Setting interval < 840s is recommended.")

    print(f"Starting keep-alive pinger for: {args.url}")
    print(f"Ping interval: {args.interval}s ({args.interval // 60}m {args.interval % 60}s)")
    print("Press Ctrl+C to terminate.")

    if args.once:
        success = ping(args.url)
        sys.exit(0 if success else 1)

    while True:
        ping(args.url)
        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeep-alive pinger stopped.")
        sys.exit(0)

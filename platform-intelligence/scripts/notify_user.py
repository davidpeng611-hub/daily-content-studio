#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV = ROOT / "config" / "notification.env"


def load_env_file(path):
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


def post_json(url, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def build_text(title, body, file_path=""):
    text = f"{title}\n\n{body}".strip()
    if file_path:
        text += f"\n\n本地报告：{file_path}"
    return text


def notify_wecom(webhook_url, title, body, file_path):
    payload = {
        "msgtype": "text",
        "text": {
            "content": build_text(title, body, file_path)
        },
    }
    return post_json(webhook_url, payload)


def notify_serverchan(sendkey, title, body, file_path):
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    payload = {
        "title": title,
        "desp": build_text(title, body, file_path),
    }
    return post_json(url, payload)


def notify_imessage(recipient, title, body, file_path):
    message = build_text(title, body, file_path)
    script = """
on run argv
  set targetBuddy to item 1 of argv
  set targetMessage to item 2 of argv
  tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetChat to buddy targetBuddy of targetService
    send targetMessage to targetChat
  end tell
end run
"""
    result = subprocess.run(
        ["osascript", "-e", script, recipient, message],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "iMessage send failed")
    return 0, result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Send platform-intelligence reports to the user's WeChat notification channel.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--file", default="")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env_file(args.env_file)

    file_path = str(Path(args.file).expanduser().resolve()) if args.file else ""
    wecom_webhook = os.environ.get("WECHAT_WORK_BOT_WEBHOOK", "").strip()
    serverchan_sendkey = os.environ.get("SERVERCHAN_SENDKEY", "").strip()
    imessage_recipient = os.environ.get("IMESSAGE_RECIPIENT", "").strip()

    if args.dry_run:
        print(build_text(args.title, args.body, file_path))
        return

    if wecom_webhook:
        status, response = notify_wecom(wecom_webhook, args.title, args.body, file_path)
        print(f"WECHAT_WORK_BOT_WEBHOOK status={status} response={response}")
        return

    if imessage_recipient:
        status, response = notify_imessage(imessage_recipient, args.title, args.body, file_path)
        print(f"IMESSAGE_RECIPIENT status={status} response={response}")
        return

    if serverchan_sendkey:
        status, response = notify_serverchan(serverchan_sendkey, args.title, args.body, file_path)
        print(f"SERVERCHAN_SENDKEY status={status} response={response}")
        return

    print(
        "No notifier configured. Set WECHAT_WORK_BOT_WEBHOOK, IMESSAGE_RECIPIENT, or SERVERCHAN_SENDKEY.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        print(f"Notify failed: {exc}", file=sys.stderr)
        sys.exit(1)

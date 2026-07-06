#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "config" / "notification.env"


def write_env(kind, value):
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    if kind == "serverchan":
        text = f'SERVERCHAN_SENDKEY="{value.strip()}"\n'
    elif kind == "wecom":
        text = f'WECHAT_WORK_BOT_WEBHOOK="{value.strip()}"\n'
    elif kind == "imessage":
        text = f'IMESSAGE_RECIPIENT="{value.strip()}"\n'
    else:
        raise ValueError(kind)
    ENV_FILE.write_text(text, encoding="utf-8")
    ENV_FILE.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description="Configure WeChat notification for platform-intelligence automations.")
    parser.add_argument("--serverchan-sendkey", help="Server酱 SendKey, usually starts with SCT")
    parser.add_argument("--wecom-webhook", help="Enterprise WeChat bot webhook URL")
    parser.add_argument("--imessage-recipient", help="iMessage recipient phone number or Apple ID email")
    parser.add_argument("--test", action="store_true", help="Send a test notification after saving")
    args = parser.parse_args()

    if args.serverchan_sendkey:
        write_env("serverchan", args.serverchan_sendkey)
        kind = "Server酱"
    elif args.wecom_webhook:
        write_env("wecom", args.wecom_webhook)
        kind = "企业微信群机器人"
    elif args.imessage_recipient:
        write_env("imessage", args.imessage_recipient)
        kind = "iMessage"
    else:
        raise SystemExit("Provide --serverchan-sendkey, --wecom-webhook, or --imessage-recipient")

    print(f"Saved {kind} notification config to {ENV_FILE}")

    if args.test:
        subprocess.run(
            [
                "python3",
                str(ROOT / "scripts" / "notify_user.py"),
                "--title",
                "每日口播工作室通知测试",
                "--body",
                "微信通知通道已经打通。以后9点复盘和12点选题会推送到这里。",
                "--file",
                str(ROOT / "README.md"),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()

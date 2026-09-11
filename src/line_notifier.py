import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAGES_URL = "https://j810225-collab.github.io/daily-financial-news/"

def format_news_for_line(digest_list):
    lines = [
        "📊 【全球每日財經焦點】",
        "─────────────────"
    ]

    for i, item in enumerate(digest_list, 1):
        lines.append(f"🔥 [{i}] {item.get('title_tw', '')}")
        lines.append(f"💡 觀點：{item.get('importance', '')}")
        
        points = item.get("key_points", [])
        for p in points:
            lines.append(f"  • {p}")
            
        lines.append(f"🔗 原文：{item.get('link', '')}")
        lines.append("")

    lines.append("─────────────────")
    lines.append(f"🌐 今日完整網頁版：{GITHUB_PAGES_URL}")
    lines.append("🤖 由 Gemini AI 自動彙整")
    return "\n".join(lines).strip()

def send_line_push(message_text):
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    targets = []

    # 支援群組 ID 與個人 User ID (以逗號分隔或分開抓取)
    group_id = os.getenv("LINE_GROUP_ID")
    user_id = os.getenv("LINE_USER_ID")

    if group_id:
        targets.extend([gid.strip() for gid in group_id.split(",") if gid.strip()])
    if user_id:
        targets.extend([uid.strip() for uid in user_id.split(",") if uid.strip()])

    # 去重
    targets = list(dict.fromkeys(targets))

    if not token or not targets:
        print("[LINE Notifier] 提示：尚未設定 LINE_CHANNEL_ACCESS_TOKEN 或目標 ID，略過 LINE 發布。")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    success = True
    for target in targets:
        payload = {
            "to": target,
            "messages": [
                {
                    "type": "text",
                    "text": message_text
                }
            ]
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                print(f"[LINE Notifier] 成功推播訊息到: {target}")
            else:
                print(f"[LINE Notifier] 推播至 {target} 失敗: HTTP {res.status_code} - {res.text}")
                success = False
        except Exception as e:
            print(f"[LINE Notifier] 連線異常 ({target}): {e}")
            success = False

    return success

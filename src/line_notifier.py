import os
import requests
from dotenv import load_dotenv

load_dotenv()

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
    lines.append("🤖 由 Gemini AI 自動彙整")
    return "\n".join(lines).strip()

def send_line_push(message_text):
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    target_id = os.getenv("LINE_GROUP_ID") or os.getenv("LINE_USER_ID")

    if not token or not target_id:
        print("[LINE Notifier] 提示：尚未設定 LINE_GROUP_ID 或 LINE_USER_ID，已略過 LINE 發布。")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "to": target_id,
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
            print("[LINE Notifier] 成功推播訊息到 LINE！")
            return True
        else:
            print(f"[LINE Notifier] 推播失敗: HTTP {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"[LINE Notifier] 連線異常: {e}")
        return False

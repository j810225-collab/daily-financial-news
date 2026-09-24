import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAGES_URL = "https://j810225-collab.github.io/daily-financial-news/"

def format_news_for_line(digest_list):
    lines = [
        "📊 【全球財經焦點速報】(每 3 日精選)",
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
    lines.append(f"🌐 完整網頁版：{GITHUB_PAGES_URL}")
    lines.append("🤖 由 Gemini AI 自動彙整")
    return "\n".join(lines).strip()

def send_line_push(message_text):
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    
    # 優先只推播給群組，避免重複發個人浪費每月 200 則的額度
    target_id = os.getenv("LINE_GROUP_ID") or os.getenv("LINE_USER_ID")

    if not token or not target_id:
        print("[LINE Notifier] 提示：尚未設定 LINE_CHANNEL_ACCESS_TOKEN 或目標 ID，略過 LINE 發布。")
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
            print(f"[LINE Notifier] 成功推播訊息到: {target_id}")
            return True
        elif res.status_code == 429:
            print(f"[LINE Notifier] 推播受限 (HTTP 429): 本月 LINE 免費 200 則額度已用完，將於下月 1 號重置。")
            return False
        else:
            print(f"[LINE Notifier] 推播至 {target_id} 失敗: HTTP {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"[LINE Notifier] 連線異常: {e}")
        return False

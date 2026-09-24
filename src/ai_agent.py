import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def summarize_financial_news(articles, top_k=4):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

    client = genai.Client(api_key=api_key)

    articles_input = []
    for idx, a in enumerate(articles, 1):
        articles_input.append(
            f"[{idx}] 媒體: {a['source']}\n"
            f"標題: {a['title']}\n"
            f"內文摘要: {a.get('summary', '')}\n"
            f"連結: {a['link']}\n"
        )
    news_text = "\n---\n".join(articles_input)

    prompt = f"""你是一位擁有 20 年經驗的華爾街與全球宏觀經濟頂級分析師。
請從以下提供的全球財經新聞中，依據「對全球市場、經濟脈動、重大產業或投資人影響力」為標準，精選出最重要的 {top_k} 則新聞。

針對挑選出的每則新聞，請輸出以下資訊（繁體中文）：
1. title_tw: 專業、精準且引人注目的繁體中文新聞標題。
2. original_title: 原始英文標題。
3. source: 來源媒體。
4. link: 原文網址。
5. importance: 為什麼這則新聞至關重要（1 句話精闢點評）。
6. key_points: 2 至 3 點核心事實與深入洞察摘要（繁體中文清單）。

請務必以嚴格的 JSON 陣列格式回傳，格式範例如下：
[
  {{
    "title_tw": "標題",
    "original_title": "Original Title",
    "source": "CNBC Finance",
    "link": "https://...",
    "importance": "核心重要性點評",
    "key_points": ["重點1", "重點2"]
  }}
]

待篩選的新聞清單：
{news_text}
"""

    # 重試 4 次，遇到尖峰 503 自動拉長等待時間
    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[AI Agent] 正在請求 Gemini 分析新聞 (第 {attempt}/{max_retries} 次)...")
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            if response and response.text:
                digest = json.loads(response.text)
                if isinstance(digest, list) and len(digest) > 0:
                    print(f"[AI Agent] 成功完成新聞精選與繁中摘要！")
                    return digest
        except Exception as e:
            print(f"[AI Agent] 呼叫異常: {e}")
            if attempt < max_retries:
                wait_sec = attempt * 8  # 8s, 16s, 24s
                print(f"[AI Agent] 等待 {wait_sec} 秒後進行重試...")
                time.sleep(wait_sec)

    # 降級保險：確保系統永遠不中斷
    print("[AI Agent] 警告：AI 模型重試後仍無法連線，啟用降級安全模式...")
    fallback_digest = []
    for a in articles[:top_k]:
        fallback_digest.append({
            "title_tw": a["title"],
            "original_title": a["title"],
            "source": a["source"],
            "link": a["link"],
            "importance": "即時國際重大新聞（AI 雲端連線忙碌中，提供原文快訊）",
            "key_points": [a.get("summary", "請點擊連結查看詳細報導。")[:100] + "..."]
        })
    return fallback_digest

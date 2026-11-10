import os
import json
import time
import random
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# 劃分兩組完全不同底層架構的算力通道，避免「同群體同時 503」
CLUSTER_LITE = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview"
]

CLUSTER_FLAGSHIP = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest"
]

def find_healthy_model(client):
    """
    健康預檢：發送微型探針，秒級找出目前最健康、不塞車的模型。
    交叉檢查 Lite 與 Flagship 兩大算力通道。
    """
    all_candidates = CLUSTER_LITE + CLUSTER_FLAGSHIP
    print("[AI Agent] 啟動模型健康預檢...")
    for model_name in all_candidates:
        try:
            # 微型探針測試
            res = client.models.generate_content(
                model=model_name,
                contents="ping",
                config=types.GenerateContentConfig(
                    max_output_tokens=5,
                    temperature=0.1
                )
            )
            if res and res.text:
                print(f"[AI Agent] 預檢通過！當前最健康模型為: {model_name}")
                return model_name
        except Exception as e:
            print(f"[AI Agent] 模型 {model_name} 暫時壅塞或不可用 ({e.__class__.__name__})，檢查下一模型...")
            continue
    return None

def summarize_financial_news(articles, top_k=4):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

    client = genai.Client(api_key=api_key)

    # 執行隨機微幅抖動（Jitter 2~8 秒），避開與其他定時排程在精確同一秒打入 API
    jitter_sec = random.uniform(2, 8)
    time.sleep(jitter_sec)

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

    # 第一輪：優先探測出的最佳健康模型
    healthy_model = find_healthy_model(client)
    prioritized_models = []
    if healthy_model:
        prioritized_models.append(healthy_model)
    # 將其餘候選模型加入備援清單（去重）
    for m in (CLUSTER_LITE + CLUSTER_FLAGSHIP):
        if m not in prioritized_models:
            prioritized_models.append(m)

    # 深層指數退避重試循環
    for model_name in prioritized_models:
        print(f"[AI Agent] 正在嘗試使用模型處理新聞摘要: {model_name} ...")
        # 針對單一模型給予最多 3 次帶退避的機會
        for attempt in range(1, 4):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                if response and response.text:
                    digest = json.loads(response.text)
                    if isinstance(digest, list) and len(digest) > 0:
                        print(f"[AI Agent] 成功使用 {model_name} 完成新聞精選與繁中摘要！")
                        return digest
            except Exception as e:
                err_str = str(e)
                print(f"[AI Agent] {model_name} 執行異常 (第 {attempt} 次): {err_str[:120]}")
                if "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str:
                    wait_sec = (attempt * 6) + random.uniform(1, 4)
                    print(f"[AI Agent] 遇到伺服器壅塞，等待 {wait_sec:.1f} 秒後進行指數退避重試...")
                    time.sleep(wait_sec)
                else:
                    # 非壅塞錯誤（如格式問題），直接切換至下一模型
                    break
        print(f"[AI Agent] {model_name} 已達到重試上限，自動切換至下一備援模型...")

    # 兜底降級保險（萬一 Google 全球網路全面中斷）
    print("[AI Agent] 警告：所有算力通道皆暫時無法連線，啟用降級安全模式...")
    fallback_digest = []
    for a in articles[:top_k]:
        fallback_digest.append({
            "title_tw": a["title"],
            "original_title": a["title"],
            "source": a["source"],
            "link": a["link"],
            "importance": "即時國際重大新聞（Google 全球服務連線短暫維護中，提供原文快訊）",
            "key_points": [a.get("summary", "請點擊連結查看詳細報導。")[:100] + "..."]
        })
    return fallback_digest

import os
import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from news_fetcher import fetch_latest_news
from ai_agent import summarize_financial_news
from web_generator import generate_html
from line_notifier import format_news_for_line, send_line_push

def main():
    print("==================================================")
    print("  [AI Agent] 啟動全球財經新聞 AI 篩選與推播系統")
    print("==================================================")

    # 1. 抓取新聞
    print("\n[步驟 1/4] 正在抓取最新國際財經新聞 (RSS)...")
    articles = fetch_latest_news(max_per_feed=4)
    print(f"-> 成功取得 {len(articles)} 篇即時國際新聞！")

    if not articles:
        print("未抓取到任何新聞，結束流程。")
        return

    # 2. Gemini AI 篩選與繁中摘要
    print("\n[步驟 2/4] 呼叫 Gemini AI 進行深度篩選、繁中翻譯與重點洞察...")
    digest = summarize_financial_news(articles, top_k=3)
    print(f"-> AI 精選出 {len(digest)} 則核心重大財經頭條！")

    # 3. 產出現代化網頁
    print("\n[步驟 3/4] 正在生成深色質感網頁 index.html ...")
    output_html_path = os.path.join(os.path.dirname(__file__), "index.html")
    generate_html(digest, output_file=output_html_path)

    # 4. 推播到 LINE
    print("\n[步驟 4/4] 正在處理 LINE 訊息推播...")
    line_msg = format_news_for_line(digest)
    send_line_push(line_msg)

    print("\n==================================================")
    print("  [完成] 今日全球財經速報處理完畢！")
    print(f"  -> 網頁已產出於: {output_html_path}")
    print("==================================================")

if __name__ == "__main__":
    main()

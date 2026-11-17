import os
import sys
import argparse

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
    parser = argparse.ArgumentParser(description="全球財經新聞 AI 篩選與推播系統")
    parser.add_argument("--skip-line", action="store_true", help="僅更新網頁內容，略過 LINE 推播")
    args = parser.parse_args()

    # 也可以透過環境變數 ENABLE_LINE_PUSH 判斷 (預設 True，若設為 'false' 則略過)
    env_enable_line = os.getenv("ENABLE_LINE_PUSH", "true").lower() != "false"
    should_send_line = not args.skip_line and env_enable_line

    print("==================================================")
    print("  [AI Agent] 啟動全球財經新聞 AI 篩選與更新系統")
    print(f"  -> 今日 LINE 推播開關: {'開啟 (每 3 日發布)' if should_send_line else '關閉 (僅更新每日網站)'}")
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

    # 3. 產出現代化網頁（每日更新）
    print("\n[步驟 3/4] 正在生成深色質感網頁 index.html ...")
    output_html_path = os.path.join(os.path.dirname(__file__), "index.html")
    generate_html(digest, output_file=output_html_path)

    # 4. 推播到 LINE（僅在排程指定日推播）
    if should_send_line:
        print("\n[步驟 4/4] 正在處理 LINE 訊息推播...")
        line_msg = format_news_for_line(digest)
        send_line_push(line_msg)
    else:
        print("\n[步驟 4/4] 今日設定為「僅更新網站」，略過 LINE 推播以保護每月額度。")

    print("\n==================================================")
    print("  [完成] 今日全球財經速報處理完畢！")
    print(f"  -> 網頁已產出於: {output_html_path}")
    print("==================================================")

if __name__ == "__main__":
    main()

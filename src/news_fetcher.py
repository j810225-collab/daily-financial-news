import feedparser
import html
import re

RSS_FEEDS = [
    {
        "source": "CNBC Finance",
        "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
    },
    {
        "source": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex"
    }
]

def clean_text(raw_html):
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", "", raw_html)
    return html.unescape(clean).strip()

def fetch_latest_news(max_per_feed=5):
    all_articles = []
    seen_titles = set()

    for feed_info in RSS_FEEDS:
        source_name = feed_info["source"]
        feed_url = feed_info["url"]
        try:
            feed = feedparser.parse(feed_url)
            count = 0
            for entry in feed.entries:
                title = clean_text(entry.get("title", ""))
                summary = clean_text(entry.get("summary", entry.get("description", "")))
                link = entry.get("link", "")
                pub_date = entry.get("published", entry.get("updated", ""))

                if not title or title in seen_titles:
                    continue

                seen_titles.add(title)
                all_articles.append({
                    "source": source_name,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": pub_date
                })
                count += 1
                if count >= max_per_feed:
                    break
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")

    return all_articles

if __name__ == "__main__":
    news = fetch_latest_news(3)
    print(f"Successfully fetched {len(news)} articles.")
    for i, a in enumerate(news[:5], 1):
        print(f"{i}. [{a['source']}] {a['title']}")

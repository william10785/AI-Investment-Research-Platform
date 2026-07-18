


def get_ticker() -> str:
    """Ask the user for a ticker and return the cleaned value."""
    #.strip() takes care of blank space
    #.upper() makes all upper case
    ticker = input("Enter Stock Ticker: ").strip().upper()
    return ticker



def validate_ticker(ticker: str) -> bool:
    """Return True when the ticker is acceptable, otherwise False."""
    if ticker == "":
        return False
    return True


def get_sample_articles(ticker: str) -> list[dict]:
    """Return a few fake articles for testing."""

    # dictionary is similar to hashmap in java
    article_1 = {
    "id" : 1,
    "ticker": ticker,
    "title": f"{ticker} announces a new product",
    "source": "Example News",
    "description": "...",
    "url": "https://example.com/article",
    "published_at": "2026-07-18"
    }

    article_2 = {
    "id" : 2,
    "ticker": ticker,
    "title": f"{ticker} announces a new technology",
    "source": "Example News",
    "description": "...",
    "url": "https://example.com/article2",
    "published_at": "2026-07-18"
    }

    articles = [article_1, article_2]
    return articles


def main() -> None:

    while True:
        ticker = get_ticker()

        if validate_ticker(ticker):
            break

        print("Ticker Required. Try Again.")
    print(f"Starting Research for {ticker}")
        
    # same as print("Starting Research for " + ticker)

    articles = get_sample_articles(ticker)

    for article in articles:
        print(f"\nTitle: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published_at']}")
        print(f"URL: {article['url']}")



if __name__ == "__main__":
    main()
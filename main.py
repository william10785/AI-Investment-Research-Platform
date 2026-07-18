


def get_ticker() -> str:
    """Ask the user for a ticker and return the cleaned value."""
    #.strip() takes care of blank space
    #.upper() makes all upper case
    ticker = input("Enter Stock Ticker: ").strip().upper()
    return ticker



def validate_ticker(ticker: str) -> bool:
    """Return True when the ticker is acceptable, otherwise False."""

    if not ticker:
        return False
    
    if len(ticker) > 10:
        return False
    
    if "-" in ticker[0] or "." in ticker[0]:
        return False
    
    if "-" in ticker[-1] or "." in ticker[-1]:
        return False
    
    if " " in ticker:
        return False
    
    if "\n" in ticker or "\t" in ticker:
        return False
    
    for character in ticker:
        is_letter_or_number = character.isalnum()
        is_allowed_separator = "-" in character or "." in character
        if not(is_letter_or_number or is_allowed_separator):
            return False
    
    prev = "empty"

    for character in ticker:
        is_prev_separator = prev in "-" or prev in "."
        is_cur_separator = character in "-" or character in "."
        if is_prev_separator and is_cur_separator:
            return False
        prev = character

    return True

"""
Reject empty input.
Reject input longer than 10 characters.
Allow letters and numbers.
Allow . and - inside the ticker.
Reject other characters, including spaces and $.
Reject a ticker beginning or ending with . or -.
Reject consecutive separators such as .., --, .-, or -..
Return only True or False; don’t print from the validation function.
"""




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

        print("Invalid Ticker. Try Again.")
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
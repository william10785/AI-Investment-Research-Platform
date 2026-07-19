
import os
import requests
import json
from dotenv import load_dotenv

def get_ticker() -> str:
    """Ask the user for a ticker and return the cleaned value."""
    # .strip() removes surrounding whitespace.
    # .upper() converts letters to uppercase.
    ticker = input("Enter Stock Ticker: ").strip().upper()
    return ticker

def validate_ticker(ticker: str) -> bool:
    """Return True when the ticker is acceptable, otherwise False."""

    separators = ".-"

    # Reject an empty string or a ticker longer than 10 characters.
    if not ticker or len(ticker) > 10:
        return False
    
    # A ticker cannot start or end with a separator.
    if ticker[0] in separators or ticker[-1] in separators:
        return False
    
    # Every character must be a letter, number, or allowed separator.
    for character in ticker:
        is_letter_or_number = character.isalnum()
        if not(is_letter_or_number or character in separators):
            return False
    
    prev = "empty"

    for character in ticker:
        is_prev_separator = prev in "-" or prev in "."
        is_cur_separator = character in "-" or character in "."
        if is_prev_separator and is_cur_separator:
            return False
        prev = character

    return True

def get_sample_articles(ticker: str) -> list[dict]:
    """Return a few fake articles for testing."""

    # A dictionary is similar to a HashMap in Java.
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

def get_api_key() -> str | None:
    load_dotenv()
    return os.getenv("FINNHUB_API_KEY")

def fetch_company_profile(ticker: str, api_key: str) -> dict | None:
    url = "https://finnhub.io/api/v1/stock/profile2"
    headers = {"X-Finnhub-Token": api_key,}
    params = {"symbol": ticker}
    if not api_key:
        print("Missing API Key")
        return
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        print("The request timed out.")
        return
    except requests.exceptions.ConnectionError:
        print("Invalid Connection")
        return
    except requests.exceptions.RequestException:
        print("External Error")
        return
    if (response.status_code == 400):
        print("Missing or Invalid Paramters in API Request")
        return
    if (response.status_code == 401):
        print("Missing or Invalid API Key")
        return
    if (response.status_code == 403):
        print("Insufficient permission")
        return
    if (response.status_code == 429):
        print("Rate Limit Exceeded")
        return
    if (500 <= response.status_code <= 599):
        print("Server side error.")
        return
    
    final_response = json.loads(response.text)
    if not final_response:
        print("Ticker does not exist")
        return
    else:
        return final_response

def extract_company_essential_data(raw_profile: dict[str, object],) -> dict[str,str] | None:
    if not raw_profile:
        return
    #selected_keys = ["ticker", "name", "exchange", "finnhubIndustry"]
    selected_keys = [("ticker", "ticker"), #listofKeys
                    ("company_name", "name"),
                    ("exchange", "exchange"),
                    ("industry", "finnhubIndustry")]
    sub_dict = {}
    for output_key, source_key in selected_keys:
        sub_dict[output_key] = raw_profile.get(source_key, "Not available")
    return sub_dict

def main() -> None:

    while True:
        ticker = get_ticker()

        if validate_ticker(ticker):
            break

        print("Invalid Ticker. Try Again.")

    print(f"Starting Research for {ticker}")
    summarized_dict = extract_company_essential_data(fetch_company_profile(ticker, get_api_key()))
    if (summarized_dict):
        print(summarized_dict)
    else:
        return

    """articles = get_sample_articles(ticker)

    for article in articles:
        print(f"\nTitle: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published_at']}")
        print(f"URL: {article['url']}") """



if __name__ == "__main__":
    main()

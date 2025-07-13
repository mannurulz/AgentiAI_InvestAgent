# data_collectors.py
import httpx
import asyncio
import json
from datetime import datetime, timedelta
from config import FINNHUB_API_KEY, QUANTUM_COMPANIES

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

async def get_stock_data(symbol: str) -> dict:
    """Fetches real-time stock quote."""
    url = f"{FINNHUB_BASE_URL}/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.RequestError as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return {}

async def get_company_news(symbol: str, lookback_days: int = 7) -> list:
    """Fetches news for a company from Finnhub within a date range."""
    today = datetime.now()
    past_date = today - timedelta(days=lookback_days)
    from_date = past_date.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    url = f"{FINNHUB_BASE_URL}/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.RequestError as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []

async def get_market_sentiment(symbol: str) -> dict:
    """Fetches Finnhub's aggregated news sentiment."""
    url = f"{FINNHUB_BASE_URL}/news-sentiment?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.RequestError as e:
        print(f"Error fetching market sentiment for {symbol}: {e}")
        return {}

async def collect_all_data(company_symbols: list) -> dict:
    """Collects stock, news, and sentiment data for all specified companies."""
    all_data = {}
    tasks = []
    for symbol in company_symbols:
        tasks.append(get_stock_data(symbol))
        tasks.append(get_company_news(symbol))
        tasks.append(get_market_sentiment(symbol)) # Finnhub has its own sentiment

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Distribute results back to companies
    for i, symbol in enumerate(company_symbols):
        stock_data = results[i*3] if not isinstance(results[i*3], Exception) else {}
        news_data = results[i*3+1] if not isinstance(results[i*3+1], Exception) else []
        sentiment_data = results[i*3+2] if not isinstance(results[i*3+2], Exception) else {}

        all_data[symbol] = {
            "stock_quote": stock_data,
            "news": news_data,
            "finnhub_sentiment": sentiment_data # Finnhub's built-in sentiment
        }
    return all_data

# Example usage (for testing data collection)
async def main_data_collector_test():
    symbols = list(QUANTUM_COMPANIES.keys())
    data = await collect_all_data(symbols)
    # print(json.dumps(data, indent=2))
    print(f"Collected data for {len(data)} companies.")
    # You'd typically log or store this data

if __name__ == "__main__":
    asyncio.run(main_data_collector_test())
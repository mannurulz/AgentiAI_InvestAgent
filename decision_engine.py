# decision_engine.py
import google.generativeai as genai
import json
from config import GEMINI_API_KEY, SENTIMENT_THRESHOLD_POSITIVE, SENTIMENT_THRESHOLD_NEGATIVE

genai.configure(api_key=GEMINI_API_KEY)

class DecisionEngine:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def get_investment_recommendation(
        self,
        company_data: dict,
        analyzed_sentiment: float,
        stock_trend: str,
        finnhub_sentiment: dict # Finnhub's aggregated sentiment
    ) -> dict:
        """
        Uses the LLM to generate an investment recommendation based on analyzed data.
        """
        company_name = company_data['name']
        company_symbol = company_data['symbol']
        company_notes = company_data['notes']

        current_price = company_data['stock_quote'].get('c', 'N/A')
        percent_change = company_data['stock_quote'].get('dp', 'N/A')

        news_headlines = [n.get('headline') for n in company_data['news'] if n.get('headline')]
        if not news_headlines:
            news_summary = "No recent news available."
        else:
            # Use LLM to summarize news if many articles, or just list a few
            news_summary_prompt = f"Summarize the following recent news headlines about {company_name} ({company_symbol}) and extract key positive or negative themes:\n\n" + "\n".join(news_headlines[:5]) # Limit to first 5 for prompt size
            news_summary_response = await self._call_llm(news_summary_prompt)
            news_summary = news_summary_response # Assuming LLM gives direct text response

        # Extract Finnhub specific sentiment details
        finnhub_buzz = finnhub_sentiment.get('buzz', {}).get('articlesInLastWeek', 'N/A')
        finnhub_sentiment_score = finnhub_sentiment.get('sentiment', {}).get('companyNewsScore', 'N/A')
        finnhub_bullish_percent = finnhub_sentiment.get('sentiment', {}).get('bullishPercent', 'N/A')


        # Prompt the LLM for a recommendation
        recommendation_prompt = f"""
        You are an expert financial analyst specializing in quantum computing.
        Your task is to provide an investment recommendation (Buy/Hold/Sell) for {company_name} ({company_symbol}), considering the following data:

        Company Overview: {company_notes}

        Current Market Data:
        - Current Price: ${current_price}
        - Daily Price Change (%): {percent_change}%
        - Recent Stock Trend (Today): {stock_trend}

        News and Sentiment:
        - Recent News Summary: {news_summary}
        - Calculated News Sentiment (from our analysis): {analyzed_sentiment:.2f} (Range -1.0 to 1.0)
        - Finnhub Aggregated News Articles (Last Week): {finnhub_buzz}
        - Finnhub Aggregated Company News Score: {finnhub_sentiment_score} (Higher is more positive)
        - Finnhub Aggregated Bullish Percent: {finnhub_bullish_percent}%

        Based on this information, provide a clear investment recommendation (BUY, HOLD, or SELL), a brief justification, and list potential risks.

        Respond in JSON format with the following structure:
        {{
            "company_symbol": "...",
            "recommendation": "BUY" | "HOLD" | "SELL",
            "justification": "...",
            "risks": ["...", "..."],
            "current_sentiment_score": ...,
            "market_trend": "...",
            "news_summary": "..."
        }}
        """

        try:
            # We enforce JSON output using `response_mime_type`
            response = await self.model.generate_content_async(
                contents=[{"role": "user", "parts": [{"text": recommendation_prompt}]}],
                generation_config={"response_mime_type": "application/json"}
            )
            # Access the text from the response and parse it
            llm_output_text = response.text
            recommendation_json = json.loads(llm_output_text)
            return recommendation_json
        except Exception as e:
            print(f"Error generating recommendation for {company_symbol} with LLM: {e}")
            print(f"LLM Output attempted to parse: {llm_output_text}") # Debugging
            return {
                "company_symbol": company_symbol,
                "recommendation": "ERROR",
                "justification": f"Failed to get LLM recommendation: {e}",
                "risks": ["API Error", "LLM parsing error"],
                "current_sentiment_score": analyzed_sentiment,
                "market_trend": stock_trend,
                "news_summary": news_summary
            }

    async def _call_llm(self, prompt: str) -> str:
        """Helper to call the LLM for general text generation."""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling LLM for general text: {e}")
            return "Error in LLM response."

# Example usage (for testing decision engine)
async def main_decision_engine_test():
    engine = DecisionEngine()
    # Mock data for a single company
    mock_company_data = {
        "symbol": "IONQ",
        "name": "IonQ",
        "notes": "Pure-play in trapped-ion quantum computing, known for high fidelity.",
        "stock_quote": {'c': 8.50, 'd': 0.20, 'dp': 2.41, 'h': 8.60, 'l': 8.30, 'o': 8.30, 'pc': 8.30, 't': 1700000000},
        "news": [
            {"headline": "IonQ announces new partnership for quantum software.", "summary": "Exciting news about collaboration."},
            {"headline": "Analyst downgrades IonQ stock due to market conditions.", "summary": "Concerns about valuation."}
        ],
        "finnhub_sentiment": {
            "buzz": {"articlesInLastWeek": 20, "weeklyAverage": 15},
            "sentiment": {"companyNewsScore": 0.6, "sectorAverageBullishPercent": 50.0, "bullishPercent": 70.0}
        }
    }
    mock_analyzed_sentiment = 0.25 # Our custom sentiment analysis
    mock_stock_trend = "positive"

    recommendation = await engine.get_investment_recommendation(
        mock_company_data,
        mock_analyzed_sentiment,
        mock_stock_trend,
        mock_company_data["finnhub_sentiment"]
    )
    print(json.dumps(recommendation, indent=2))

if __name__ == "__main__":
    asyncio.run(main_decision_engine_test())
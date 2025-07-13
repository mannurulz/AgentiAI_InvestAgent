# main_agent.py
import asyncio
import json
from datetime import datetime
from config import QUANTUM_COMPANIES
from data_collectors import collect_all_data
from analyzers import Analyzer
from decision_engine import DecisionEngine
from memory import AgentMemory
# from apscheduler.schedulers.asyncio import AsyncIOScheduler # Uncomment for scheduling

class InvestmentAgent:
    def __init__(self):
        self.companies = QUANTUM_COMPANIES
        self.collector = None # Will be initialized in run()
        self.analyzer = Analyzer()
        self.decision_engine = DecisionEngine()
        self.memory = AgentMemory()

    async def run_analysis_cycle(self):
        print(f"\n--- Running Investment Agent Analysis Cycle ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")

        # 1. Perception: Collect Data
        company_symbols = list(self.companies.keys())
        raw_data = await collect_all_data(company_symbols)
        # print("DEBUG: Raw data collected.")
        # print(json.dumps(raw_data, indent=2)) # For debugging

        recommendations = {}
        for symbol, data in raw_data.items():
            company_info = self.companies[symbol]
            company_info["symbol"] = symbol # Add symbol for easier access

            # Ensure 'stock_quote' exists before proceeding
            if not data.get('stock_quote'):
                print(f"Skipping {symbol}: No stock data available.")
                continue

            company_info["stock_quote"] = data["stock_quote"]
            company_info["news"] = data["news"]
            company_info["finnhub_sentiment"] = data["finnhub_sentiment"]

            # 2. Reasoning (Analysis): Process Data
            news_sentiment_score = self.analyzer.analyze_news_sentiment(data["news"])
            stock_trend = self.analyzer.analyze_stock_trend(data["stock_quote"])

            # 3. Reasoning (Decision): Get Recommendation
            print(f"\n--- Analyzing {company_info['name']} ({symbol}) ---")
            recommendation = await self.decision_engine.get_investment_recommendation(
                company_info,
                news_sentiment_score,
                stock_trend,
                data["finnhub_sentiment"]
            )
            recommendations[symbol] = recommendation
            # Store the recommendation in memory
            self.memory.update_company_data(symbol, {"latest_recommendation": recommendation, "last_updated": datetime.now().isoformat()})

        # 4. Action: Report Recommendations
        print("\n" + "="*70)
        print("                   Investment Agent Recommendations                   ")
        print("="*70)
        for symbol, rec in recommendations.items():
            print(f"\nCompany: {self.companies[symbol]['name']} ({rec.get('company_symbol')})")
            print(f"Recommendation: {rec.get('recommendation')}")
            print(f"Justification: {rec.get('justification')}")
            print(f"Risks: {', '.join(rec.get('risks', []))}")
            # print(f"Sentiment Score: {rec.get('current_sentiment_score'):.2f}") # From our analysis
            # print(f"Market Trend: {rec.get('market_trend')}")
            # print(f"News Summary: {rec.get('news_summary')}")
            print("-" * 60)

        print(f"\n--- Analysis Cycle Completed ---")

async def main():
    agent = InvestmentAgent()

    # To run once
    await agent.run_analysis_cycle()

    # To run periodically (uncomment and adjust interval)
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(agent.run_analysis_cycle, 'interval', hours=24) # Run every 24 hours
    # print("Agent scheduled to run every 24 hours. Press Ctrl+C to exit.")
    # scheduler.start()
    # try:
    #     while True:
    #         await asyncio.sleep(3600) # Keep main thread alive
    # except (KeyboardInterrupt, SystemExit):
    #     scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
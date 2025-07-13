# config.py
GEMINI_API_KEY = "MANNU MANNU MANNU"
FINNHUB_API_KEY = "MANNU MANNU MANNU" # Or Alpha Vantage/NewsAPI.org key
#https://finnhub.io/dashboard

# Companies to track (use their stock symbols)
QUANTUM_COMPANIES = {
    "IBM": {"name": "IBM", "sector": "Tech, diversified", "notes": "Superconducting qubits, IBM Quantum Experience"},
    "IONQ": {"name": "IonQ", "sector": "Quantum Computing (Trapped-ion)", "notes": "Pure-play, high fidelity"},
    "QBTS": {"name": "D-Wave Quantum Inc.", "sector": "Quantum Computing (Annealing)", "notes": "Optimization problems"},
    "RGTI": {"name": "Rigetti Computing", "sector": "Quantum Computing (Superconducting)", "notes": "Hybrid systems"},
    "GOOGL": {"name": "Alphabet Inc. (Google)", "sector": "Tech, diversified", "notes": "Quantum AI, Sycamore processor"},
    "MSFT": {"name": "Microsoft Corp.", "sector": "Tech, diversified", "notes": "Azure Quantum, topological qubits research"},
    # Add more companies as needed
}

# Thresholds for sentiment/recommendation (adjust these based on testing)
SENTIMENT_THRESHOLD_POSITIVE = 0.1
SENTIMENT_THRESHOLD_NEGATIVE = -0.05
# Add more configuration, e.g., data refresh interval, report output path
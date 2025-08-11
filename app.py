import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="DCA & Monte Carlo Simulator", layout="wide")

st.title("📈 DCA & Monte Carlo Investment Simulator")

# Sidebar inputs
ticker = st.sidebar.text_input("Stock/ETF Ticker", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", datetime(2015, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.today())

schedule = st.sidebar.selectbox("DCA Schedule", ["Monthly", "Weekly", "Custom Dates"])
investment_amount = st.sidebar.number_input("Investment per Period ($)", value=500)

# Monte Carlo parameters
st.sidebar.subheader("Monte Carlo Simulation")
mc_mu = st.sidebar.number_input("Expected Return (mu)", value=0.07, step=0.01)
mc_sigma = st.sidebar.number_input("Volatility (sigma)", value=0.15, step=0.01)
mc_sims = st.sidebar.number_input("Number of Simulations", value=1000, step=100)

# Fetch data
st.subheader(f"Fetching data for {ticker}...")
data = yf.download(ticker, start=start_date, end=end_date)
if data.empty:
    st.error("No data found. Try a different ticker or date range.")
    st.stop()

data["Return"] = data["Adj Close"].pct_change()

# DCA calculation
if schedule == "Monthly":
    invest_dates = pd.date_range(start=start_date, end=end_date, freq='M')
elif schedule == "Weekly":
    invest_dates = pd.date_range(start=start_date, end=end_date, freq='W')
else:
    invest_dates = st.sidebar.date_input("Select Custom Investment Dates", [])
    if not invest_dates:
        st.warning("Please select at least one custom date.")
        st.stop()

portfolio_value = 0
shares = 0
for date in invest_dates:
    if date in data.index:
        close_price = data.loc[date, "Adj Close"]
    else:
        # Pick nearest available trading date
        close_price = data["Adj Close"].loc[:date].iloc[-1]
    shares_bought = investment_amount / close_price
    shares += shares_bought
    portfolio_value = shares * data["Adj Close"].iloc[-1]

st.subheader("📊 DCA Results")
st.write(f"Total Shares: {shares:.2f}")
st.write(f"Portfolio Value: ${portfolio_value:,.2f}")
st.write(f"Total Invested: ${len(invest_dates) * investment_amount:,.2f}")
st.write(f"Profit/Loss: ${portfolio_value - len(invest_dates) * investment_amount:,.2f}")

# Plot DCA
fig, ax = plt.subplots()
ax.plot(data.index, data["Adj Close"], label=f"{ticker} Price")
ax.set_title("Price History")
ax.legend()
st.pyplot(fig)

# Monte Carlo Simulation
st.subheader("🎲 Monte Carlo Simulation")
sim_days = 252  # trading days
results = []
for _ in range(mc_sims):
    prices = [data["Adj Close"].iloc[-1]]
    for _ in range(sim_days):
        prices.append(prices[-1] * np.exp((mc_mu - 0.5 * mc_sigma**2) + mc_sigma * np.random.normal()))
    results.append(prices[-1])

st.write(f"Mean Final Price: ${np.mean(results):.2f}")
st.write(f"5% Quantile: ${np.percentile(results, 5):.2f}")
st.write(f"95% Quantile: ${np.percentile(results, 95):.2f}")

fig2, ax2 = plt.subplots()
ax2.hist(results, bins=50, color="skyblue", edgecolor="black")
ax2.axvline(np.mean(results), color="red", linestyle="--", label="Mean")
ax2.set_title("Monte Carlo Simulation Results")
ax2.legend()
st.pyplot(fig2)

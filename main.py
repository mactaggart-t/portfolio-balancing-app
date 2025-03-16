import json
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

# Function to get stock info
def get_stock_info(stock):
    try:
        ticker = stock["ticker"]
        shares = stock["shares"]
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = info.get("regularMarketPrice")
        pe_ratio = info.get("trailingPE")
        market_cap = info.get("marketCap")
        sector = info.get("sector")
        industry = info.get("industry")
        dividend_yield = info.get("dividendYield")
        dividend_rate = info.get("dividendRate")

        if not sector or sector in ["N/A", "None"]:
            sector = "ETF"

        total_value = current_price * shares if current_price else None

        return {
            "Ticker": ticker,
            "Shares Owned": shares,
            "Current Price": current_price,
            "Total Value": total_value,
            "P/E Ratio": pe_ratio,
            "Market Cap": market_cap,
            "Sector": sector,
            "Industry": industry,
            "Dividend Yield": dividend_yield,
            "Dividend Rate": dividend_rate
        }
    
    except Exception as e:
        return {"Ticker": ticker, "Error": str(e)}

def create_two_axis_chart(df, by="Ticker"):
    df = df.sort_values(by="Total Value", ascending=False)

    total_portfolio_value = df["Total Value"].sum()
    df["Percentage of Portfolio"] = (df["Total Value"] / total_portfolio_value) * 100

    # 🔹 Bar Chart: Market Value of Each Security
    fig, ax1 = plt.subplots(figsize=(10, 5))
    plt.bar(df[by], df["Total Value"], color='skyblue')

    # Labels & Title
    ax1.bar(df[by], df["Total Value"], color='skyblue', label="Market Value ($)")
    ax1.set_ylabel("Market Value ($)")
    ax1.set_xlabel("Stock Ticker")

    # Secondary Y-axis: Percentage of Portfolio (Line Chart)
    ax2 = ax1.twinx()
    ax2.plot(df[by], df["Percentage of Portfolio"], color='red', marker='o', linestyle='dashed', label="Portfolio %")
    ax2.set_ylabel("Percentage of Total Portfolio (%)")
    plt.title(f"Market Value & Portfolio Allocation - Total Portfolio Value: ${total_portfolio_value:,.2f}")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    ax1.set_xticks(range(len(df[by])))  # Set ticks to match the number of stocks
    ax1.set_xticklabels(df[by], rotation=45, ha="right") 

def get_stock_data():
    # Read stock data from JSON file
    with open("stocks.json", "r") as file:
        stock_data = json.load(file)["stocks"]

    # Fetch stock info for each stock
    with ThreadPoolExecutor(max_workers=5) as executor:
        stock_records = list(executor.map(get_stock_info, stock_data))

    # Convert to pandas DataFrame
    return pd.DataFrame(stock_records)

def main():
    df = get_stock_data()
    df = df.dropna(subset=["Total Value"])
    sector_df = df.groupby("Sector", as_index=False).agg({"Total Value": "sum"})
    
    # create_two_axis_chart(df)
    # create_two_axis_chart(sector_df, "Sector")
    # plt.show()

    df.to_json("stock_data.json", orient="records", indent=4)
    sector_df.to_json("sector_data.json", orient="records", indent=4)

if __name__ == '__main__':
    main()
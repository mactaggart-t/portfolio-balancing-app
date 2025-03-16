import json
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor

# Function to get stock info
def get_stock_info(stock):
    try:
        ticker = stock["ticker"]
        shares = stock["shares"]
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = info.get("regularMarketPrice")
        company_name = info.get("shortName")
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
            "Company Name": company_name,
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
    df = df.sort_values(by="Total Value", ascending=False)

    total_portfolio_value = df["Total Value"].sum()
    df["Percentage of Portfolio"] = (df["Total Value"] / total_portfolio_value) * 100
    sector_df = df.groupby("Sector", as_index=False).agg({"Total Value": "sum"})
    sector_df = sector_df.sort_values(by="Total Value", ascending=False)

    total_portfolio_value = sector_df["Total Value"].sum()
    sector_df["Percentage of Portfolio"] = (sector_df["Total Value"] / total_portfolio_value) * 100

    df.to_json("stock_data.json", orient="records", indent=4)
    sector_df.to_json("sector_data.json", orient="records", indent=4)

if __name__ == '__main__':
    main()
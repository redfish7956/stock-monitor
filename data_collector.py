import yfinance as yf
from FinMind.data import DataLoader
import pandas as pd
import os
import json
from datetime import datetime

# 1. 初始化 FinMind API (記得在環境變數或專案設定中處理好 Token)
dl = DataLoader()

def get_market_metrics(ticker_code):
    """ 路徑一：yfinance 獲取量價與財報指標 """
    stock = yf.Ticker(f"{ticker_code}.TW")
    hist = stock.history(period="1d")
    info = stock.info
    return {
        '收盤價': hist['Close'].iloc[-1],
        '漲跌幅': info.get('regularMarketChangePercent', 0.0),
        '成交量': hist['Volume'].iloc[-1],
        '本益比': info.get('trailingPE', 0.0)
    }

def get_chip_data(ticker_code):
    """ 路徑二：FinMind 獲取籌碼數據 """
    # 這裡抓取法人買賣超
    df = dl.taiwan_stock_institutional_investors(ticker=ticker_code)
    return df['buy_sell_difference'].iloc[-1] if not df.empty else 0.0

def run_etl_pipeline(ticker_list=['2330']):
    """ 核心 ETL 整合程序 """
    final_data = []
    for ticker in ticker_list:
        try:
            metrics = get_market_metrics(ticker)
            chip = get_chip_data(ticker)
            
            row = {
                '代號': ticker,
                **metrics,
                '主力淨買超': chip,
                '更新時間': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            final_data.append(row)
        except Exception as e:
            print(f"代號 {ticker} 更新失敗: {e}")
            
    # 寫入邏輯
    df_final = pd.DataFrame(final_data)
    df_final.to_csv('final_database.csv', index=False)
    print("ETL 資料流更新完成。")

if __name__ == "__main__":
    # 這裡填入你想監控的股票清單
    run_etl_pipeline(['2330', '7769'])
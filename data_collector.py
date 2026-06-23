import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime
import os
import sys

# 登入設定
token = os.environ.get('FINMIND_TOKEN')
dl = DataLoader()
dl.login_by_token(api_token=token)

def get_full_market_data():
    # 取得今天日期
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"【ETL 紀錄】開始抓取日期: {date_str} 的全台股資料...")
    
    # 1. 抓取行情 (修正：全台股集體抓取必須使用 taiwan_stock_daily)
    df_price = dl.taiwan_stock_daily(date=date_str)
    
    if df_price.empty:
        print(f"【警告】{date_str} 沒有行情資料。可能原因：今天不是交易日（週末/假日），或台股尚未收盤盤後資料未更新。")
        return pd.DataFrame()
    
    # 2. 抓取基本面 (包含 stock_name, industry_cat, PE)
    df_basic = dl.taiwan_stock_info()
    
    # 3. 抓取籌碼
    df_chip = dl.taiwan_stock_institutional_investors(date=date_str)
    
    # --- 資料整合 ---
    # 先以行情為基礎
    df = df_price.merge(df_basic[['stock_id', 'stock_name', 'industry_cat', 'PE']], on='stock_id', how='left')
    
    # 再併入籌碼 (注意處理重複欄位)
    if not df_chip.empty:
        df = df.merge(df_chip[['stock_id', 'buy_sell_difference']], on='stock_id', how='left')
    else:
        df['buy_sell_difference'] = 0
        
    # --- 欄位整理 ---
    final_df = pd.DataFrame({
        '代號': df['stock_id'],
        '名稱': df['stock_name'],
        '產業別': df['industry_cat'],
        '收盤價': df['close'],
        '漲跌幅': df['spread'], 
        '成交量': df['Trading_Volume'],
        '成交量倍數': 1.0, # 暫時維持 1.0
        '本益比': df['PE'].fillna(0),
        '主力淨買超': df['buy_sell_difference'].fillna(0),
        '更新時間': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return final_df

def run_etl_pipeline():
    try:
        print("開始執行全台股 ETL...")
        df = get_full_market_data()
        
        if df.empty:
            print("【終止】由於今天沒有任何市場資料產出，本次不更新 CSV。")
            return
            
        # 存檔
        df.to_csv('final_database.csv', index=False, encoding='utf-8-sig')
        print(f"【成功】成功寫入 {len(df)} 筆最新資料到 final_database.csv")
        
    except Exception as e:
        print(f"【嚴重錯誤】ETL 過程中斷: {e}")
        # 【關鍵關鍵】：要把錯誤拋給 GitHub Actions，讓自動化管線在出錯時變紅燈，你才看得到真實報錯！
        raise e

if __name__ == "__main__":
    run_etl_pipeline()

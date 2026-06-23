import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime
import os

# 登入設定
token = os.environ.get('FINMIND_TOKEN')
dl = DataLoader()
dl.login_by_token(api_token=token)

def get_full_market_data():
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 抓取行情
    df_price = dl.taiwan_stock_daily_adj(date=date_str)
    
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
        # 存檔
        df.to_csv('final_database.csv', index=False, encoding='utf-8-sig')
        print(f"成功寫入 {len(df)} 筆資料到 final_database.csv")
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    run_etl_pipeline()

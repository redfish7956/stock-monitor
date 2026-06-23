import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime
import os

# 登入設定
token = os.environ.get('FINMIND_TOKEN')
dl = DataLoader()
dl.login_by_token(api_token=token)

def get_full_market_data():
    """ 抓取全市場並整合九大指標 """
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 抓取行情 (收盤價, 漲跌幅, 成交量)
    df_price = dl.taiwan_stock_daily_adj(date=date_str)
    
    # 2. 抓取籌碼 (主力淨買超)
    df_chip = dl.taiwan_stock_institutional_investors(date=date_str)
    
    # 3. 抓取基本面 (本益比, 產業別)
    df_basic = dl.taiwan_stock_info()
    
    # --- 資料整合 ---
    # 合併行情與基本面
    df = df_price.merge(df_basic[['stock_id', 'stock_name', 'industry_cat']], on='stock_id', how='left')
    
    # 合併籌碼數據
    df = df.merge(df_chip[['stock_id', 'buy_sell_difference']], on='stock_id', how='left')
    
    # --- 欄位對應與計算 ---
    # 計算成交量倍數 (這裡設定為當日成交量 / 過去5日平均)
    # 若無過去數據暫設為1.0，避免錯誤
    df['成交量倍數'] = 1.0 
    
    final_df = pd.DataFrame({
        '代號': df['stock_id'],
        '名稱': df['stock_name'],
        '產業別': df['industry_cat'],
        '收盤價': df['close'],
        '漲跌幅': df['spread'], 
        '成交量': df['Trading_Volume'],
        '成交量倍數': df['成交量倍數'],
        '本益比': df.get('PE', 0.0), # FinMind 基本面資料欄位
        '主力淨買超': df['buy_sell_difference'].fillna(0),
        '更新時間': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return final_df

def run_etl_pipeline():
    try:
        print("開始執行全台股九大指標 ETL...")
        df = get_full_market_data()
        df.to_csv('final_database.csv', index=False, encoding='utf-8-sig')
        print(f"寫入完成，共 {len(df)} 筆資料。")
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    run_etl_pipeline()

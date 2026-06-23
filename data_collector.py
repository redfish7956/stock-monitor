import pandas as pd
from datetime import datetime

# 簡單測試：直接寫入一行資料，排除 API 錯誤
data = [{
    '代號': '2330', '名稱': '台積電', '產業別': '半導體', 
    '收盤價': 900, '漲跌幅': 0.0, '成交量': 1000, 
    '成交量倍數': 1.0, '本益比': 20, '主力淨買超': 500, 
    '更新時間': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}]

df = pd.DataFrame(data)
df.to_csv('final_database.csv', index=False, encoding='utf-8-sig')
print("測試資料已寫入")

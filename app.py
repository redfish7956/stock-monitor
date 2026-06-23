import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- 系統設定 ---
st.set_page_config(layout="wide", page_title="台股爆量監測系統")

# 1. 密碼保護機制
def check_password():
    if "password_correct" not in st.session_session:
        st.session_session["password_correct"] = False
    
    if not st.session_session["password_correct"]:
        pwd = st.text_input("請輸入系統訪問密碼", type="password")
        if pwd == "你的專屬密碼": # 需根據實際設定調整
            st.session_session["password_correct"] = True
            st.rerun()
        st.stop()

# 2. 數據載入與狀態讀取 (對接 ETL 架構)
def load_data_and_meta():
    if not os.path.exists('final_database.csv') or not os.path.exists('meta_data.json'):
        return None, None
    df = pd.read_csv('final_database.csv')
    with open('meta_data.json', 'r') as f:
        meta = json.load(f)
    return df, meta

# --- 介面實作 ---
check_password()
df, meta = load_data_and_meta()

# 狀態儀表板
st.sidebar.title("狀態儀表板")
if meta:
    st.sidebar.info(f"量價更新：{meta.get('量價', 'N/A')}\n\n籌碼更新：{meta.get('籌碼', 'N/A')}")
else:
    st.sidebar.error("資料庫異常，請檢查後端 ETL 狀態")

st.sidebar.header("篩選條件")
show_all = st.sidebar.checkbox("無條件顯示全市場")
disable_filters = show_all

if show_all:
    st.sidebar.warning("⚠️ 全市場模式已開啟，條件篩選器已鎖定")

# 六大篩選器 (含 i 圖示說明邏輯)
vol_days = st.sidebar.number_input("連續 N 日成交量 (張)", 1, 60, 5, disabled=disable_filters, help="邏輯：統計近N日成交量是否大於設定張數")
vol_ratio = st.sidebar.number_input("成交量倍數 (X倍)", 1.0, 10.0, 2.0, disabled=disable_filters, help="邏輯：今日成交量 / 前N日均量")
pe_max = st.sidebar.number_input("本益比上限 (倍)", 1, 100, 25, disabled=disable_filters, help="邏輯：讀取當季末本益比數據")
price_high = st.sidebar.number_input("收盤價創 N 日新高", 1, 200, 20, disabled=disable_filters, help="邏輯：今日收盤價 >= 過去N日最高價")
eps_val = st.sidebar.number_input("EPS 門檻 (元)", 0.0, 50.0, 1.0, disabled=disable_filters, help="邏輯：連續N季單季EPS大於此數值")
chip_val = st.sidebar.number_input("主力買超創 N 日新高 (張)", 0, 10000, 500, disabled=disable_filters, help="邏輯：主力淨買超數值創N日新高")

# --- 資料處理邏輯 ---
if df is not None:
    if show_all:
        st.header("全市場數據")
        st.dataframe(df)
    elif any([vol_days, vol_ratio, pe_max, price_high, eps_val, chip_val]):
        # AND 交集運算
        mask = (df['量倍數'] >= vol_ratio) & (df['本益比'] <= pe_max) # 此處為範例邏輯
        filtered_df = df[mask]
        
        st.header(f"篩選結果 (共 {len(filtered_df)} 檔)")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.write("請設定篩選條件或開啟全市場顯示以查看報表。")
else:
    st.error("暫無數據，請確認 ETL 流程是否已產生 final_database.csv")
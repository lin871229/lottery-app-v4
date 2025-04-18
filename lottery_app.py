# app.py
import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz
import io

st.set_page_config(page_title="機構抽籤系統", layout="wide")
st.title("🚐 長照服務單位抽籤系統（高雄）")

tz = pytz.timezone("Asia/Taipei")

# 初始化狀態
if 'history' not in st.session_state:
    st.session_state.history = []

# 高雄區域名單
kao_areas = [
    "鹽埕區", "鼓山區", "左營區", "楠梓區", "三民區", "新興區", "前金區",
    "苓雅區", "前鎮區", "旗津區", "小港區", "鳳山區", "林園區", "大寮區",
    "大樹區", "大社區", "仁武區", "鳥松區", "岡山區", "橋頭區", "燕巢區",
    "田寮區", "阿蓮區", "路竹區", "湖內區", "茄萣區", "永安區", "彌陀區",
    "梓官區", "旗山區", "美濃區", "六龜區", "甲仙區", "杉林區", "內門區",
    "茂林區", "桃源區", "那瑪夏區"
]

st.markdown("---")

# 上傳交通接送 Excel
st.header("🚐 抽籤：交通接送服務單位")
transport_file = st.file_uploader("請上傳【交通接送】特約單位 Excel 檔案：", type=["xlsx"], key="transport")

if transport_file:
    xls = pd.ExcelFile(transport_file)
    sheet = xls.sheet_names[0]  # 預設第一個工作表
    df_transport = xls.parse(sheet)

    # 假設欄位包含：單位名稱、服務區域、電話、地址（可依實際調整）
    df_transport.columns = df_transport.columns.str.strip()

    if "服務區域" in df_transport.columns:
        area_selected = st.selectbox("請選擇區域：", kao_areas, key="transport_area")
        count = st.number_input("請選擇要抽出的單位數（1或2）：", 1, 2, 1, key="transport_count")

        df_match = df_transport[df_transport["服務區域"].astype(str).str.contains(area_selected)]
        used_names = [h['單位名稱'] for h in st.session_state.history if h['抽籤欄位'] == '交通接送']
        available = df_match[~df_match["單位名稱"].isin(used_names)]

        if st.button("開始抽籤（交通接送）"):
            if len(available) >= count:
                drawn = available.sample(n=count)
                now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                for _, row in drawn.iterrows():
                    st.session_state.history.append({
                        "單位名稱": row["單位名稱"],
                        "抽籤欄位": "交通接送",
                        "抽籤區域": area_selected,
                        "抽選時間": now
                    })
                st.success("✅ 抽籤成功！")
                st.dataframe(drawn.reset_index(drop=True), use_container_width=True)
            else:
                st.warning("🚫 該區域可抽單位不足。")
    else:
        st.error("❌ 找不到『服務區域』欄位，請檢查 Excel 檔案格式。")

# 歷史紀錄
if st.session_state.history:
    st.markdown("---")
    st.subheader("📋 歷史抽籤結果")
    df_hist = pd.DataFrame(st.session_state.history)
    with st.expander("點此展開歷史記錄"):
        st.dataframe(df_hist, use_container_width=True)

        # 匯出 Excel
        excel_buf = io.BytesIO()
        df_hist.to_excel(excel_buf, index=False, engine='openpyxl')
        excel_buf.seek(0)
        st.download_button(
            label="📥 下載歷史抽籤紀錄 Excel",
            data=excel_buf,
            file_name="抽籤紀錄.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

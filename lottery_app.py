import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# 設定台北時間
taipei_tz = pytz.timezone('Asia/Taipei')

st.set_page_config(page_title="機構抽籤系統", layout="wide")
st.title("🏠 特約機構抽籤系統")

# 上傳 Excel 檔案
uploaded_file = st.file_uploader("請上傳特約機構名冊 Excel 檔案", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = "本市113年7月1日起特約居家式長照機構名冊"
    df_raw = xls.parse(sheet_name)

    # 清理資料
    df = df_raw.iloc[2:].copy()
    df.columns = [
        "編號", "備註", "單位名稱", "設立區域", "地址", "電話", "Email",
        "長照服務項目", "居家服務履約區域", "居家喘息服務履約區域",
        "短照喘息服務履約區域", "服務時段", "承辦人員"
    ]

    # 高雄市38區
    kaohsiung_areas = [
        "鹽埕區", "鼓山區", "左營區", "楠梓區", "三民區", "新興區", "前金區",
        "苓雅區", "前鎮區", "旗津區", "小港區", "鳳山區", "林園區", "大寮區",
        "大樹區", "大社區", "仁武區", "鳥松區", "岡山區", "橋頭區", "燕巢區",
        "田寮區", "阿蓮區", "路竹區", "湖內區", "茄萣區", "永安區", "彌陀區",
        "梓官區", "旗山區", "美濃區", "六龜區", "甲仙區", "杉林區", "內門區",
        "茂林區", "桃源區", "那瑪夏區"
    ]

    # 萃取區域選項
    area_cols = ["居家喘息服務履約區域", "短照喘息服務履約區域"]
    all_area_texts = df[area_cols[0]].fillna('') + '\\n' + df[area_cols[1]].fillna('')
    split_texts = all_area_texts.str.split('[、，\\n()（）]')
    all_areas = set()
    for lst in split_texts:
        all_areas.update([a.strip() for a in lst if a and "區" in a and a in kaohsiung_areas])
    area_options = sorted(all_areas)

    # 初始化狀態
    if 'used_respite' not in st.session_state:
        st.session_state.used_respite = set()
    if 'used_shortterm' not in st.session_state:
        st.session_state.used_shortterm = set()
    if 'history' not in st.session_state:
        st.session_state.history = []

    # 抽籤區：居家喘息
    area_respite = st.sidebar.selectbox("居家喘息區域", area_options, key="respite_area")
    if st.sidebar.button("抽籤（居家喘息）"):
        df_match = df[df["居家喘息服務履約區域"].fillna('').str.contains(area_respite)]
        available = df_match[~df_match["單位名稱"].isin(st.session_state.used_respite)]
        if not available.empty:
            drawn = available.sample(1)
            unit = drawn["單位名稱"].iloc[0]
            st.session_state.used_respite.add(unit)
            st.success(f"✅ 抽中：{unit}")
            timestamp = datetime.now(taipei_tz).strftime('%Y-%m-%d %H:%M:%S')
            st.session_state.history.append({
                "單位名稱": unit,
                "抽籤欄位": "居家喘息",
                "抽籤區域": area_respite,
                "抽選時間": timestamp
            })
            st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]])
        else:
            st.warning("🚫 該區域已無可抽單位。")

    # 抽籤區：短照喘息
    area_short = st.sidebar.selectbox("短照喘息區域", area_options, key="shortterm_area")
    if st.sidebar.button("抽籤（短照喘息）"):
        df_match = df[df["短照喘息服務履約區域"].fillna('').str.contains(area_short)]
        available = df_match[~df_match["單位名稱"].isin(st.session_state.used_shortterm)]
        if not available.empty:
            drawn = available.sample(1)
            unit = drawn["單位名稱"].iloc[0]
            st.session_state.used_shortterm.add(unit)
            st.success(f"✅ 抽中：{unit}")
            timestamp = datetime.now(taipei_tz).strftime('%Y-%m-%d %H:%M:%S')
            st.session_state.history.append({
                "單位名稱": unit,
                "抽籤欄位": "短照喘息",
                "抽籤區域": area_short,
                "抽選時間": timestamp
            })
            st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]])
        else:
            st.warning("🚫 該區域已無可抽單位。")

    # 展開式歷史紀錄
    if st.session_state.history:
        st.markdown("---")
        with st.expander("📋 歷史抽籤結果（點我展開）", expanded=False):
            history_df = pd.DataFrame(st.session_state.history)
            st.dataframe(history_df, use_container_width=True)

else:
    st.info("📂 請先上傳 Excel 檔案。")

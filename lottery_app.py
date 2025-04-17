import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# 設定台北時間
taipei_tz = pytz.timezone('Asia/Taipei')
now = datetime.now(taipei_tz)

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

    # 正確的高雄市38區行政區名單
    kaohsiung_areas = [
        "鹽埕區", "鼓山區", "左營區", "楠梓區", "三民區", "新興區", "前金區",
        "苓雅區", "前鎮區", "旗津區", "小港區", "鳳山區", "林園區", "大寮區",
        "大樹區", "大社區", "仁武區", "鳥松區", "岡山區", "橋頭區", "燕巢區",
        "田寮區", "阿蓮區", "路竹區", "湖內區", "茄萣區", "永安區", "彌陀區",
        "梓官區", "旗山區", "美濃區", "六龜區", "甲仙區", "杉林區", "內門區",
        "茂林區", "桃源區", "那瑪夏區"
    ]

    # 擷取資料中符合高雄區域的區名
    area_cols = ["居家喘息服務履約區域", "短照喘息服務履約區域"]
    all_area_texts = df[area_cols[0]].fillna('') + '\\n' + df[area_cols[1]].fillna('')
    split_texts = all_area_texts.str.split('[、，\\n()（）]')
    all_areas = set()
    for lst in split_texts:
        all_areas.update([a.strip() for a in lst if a and "區" in a and a in kaohsiung_areas])
    area_options = sorted(all_areas)

    # 初始化抽籤紀錄
    if 'used_respite' not in st.session_state:
        st.session_state.used_respite = set()
    if 'used_shortterm' not in st.session_state:
        st.session_state.used_shortterm = set()

    # 初始化抽籤歷史紀錄
    if 'respites_history' not in st.session_state:
        st.session_state.respites_history = []
    if 'shortterms_history' not in st.session_state:
        st.session_state.shortterms_history = []

    # Sidebar 抽籤控制
    area_respite = st.sidebar.selectbox("居家喘息", area_options, key="respite_area")
    if st.sidebar.button("抽籤", key="draw_respite"):
        df_match = df[df["居家喘息服務履約區域"].fillna('').str.contains(area_respite)]
        available = df_match[~df_match["單位名稱"].isin(st.session_state.used_respite)]
        if len(available) > 0:
            drawn = available.sample(n=1, random_state=random.randint(1, 9999))
            st.session_state.used_respite.add(drawn["單位名稱"].iloc[0])
            # 顯示抽中的單位名稱及抽籤區域
            st.success(f"✅ 抽中單位：{drawn['單位名稱'].iloc[0]}")
            st.info(f"來自抽籤區域：{area_respite} (抽選時間：{now.strftime('%Y-%m-%d %H:%M:%S')})")
            st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))

            # 將抽中的結果記錄到歷史中
            st.session_state.respites_history.append({
                "單位名稱": drawn["單位名稱"].iloc[0],
                "抽籤欄位": "居家喘息",
                "抽籤區域": area_respite,
                "抽選時間": now.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            st.warning(f"🚫 居家喘息【{area_respite}】已無可抽籤機構。")

    area_shortterm = st.sidebar.selectbox("短照喘息", area_options, key="shortterm_area")
    if st.sidebar.button("抽籤", key="draw_shortterm"):
        df_match = df[df["短照喘息服務履約區域"].fillna('').str.contains(area_shortterm)]
        available = df_match[~df_match["單位名稱"].isin(st.session_state.used_shortterm)]
        if len(available) > 0:
            drawn = available.sample(n=1, random_state=random.randint(1, 9999))
            st.session_state.used_shortterm.add(drawn["單位名稱"].iloc[0])
            # 顯示抽中的單位名稱及抽籤區域
            st.success(f"✅ 抽中單位：{drawn['單位名稱'].iloc[0]}")
            st.info(f"來自抽籤區域：{area_shortterm} (抽選時間：{now.strftime('%Y-%m-%d %H:%M:%S')})")
            st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))

            # 將抽中的結果記錄到歷史中
            st.session_state.shortterms_history.append({
                "單位名稱": drawn["單位名稱"].iloc[0],
                "抽籤欄位": "短照喘息",
                "抽籤區域": area_shortterm,
                "抽選時間": now.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            st.warning(f"🚫 短照喘息【{area_shortterm}】已無可抽籤機構。")

    # 顯示抽籤歷史
    if st.session_state.respites_history or st.session_state.shortterms_history:
        st.subheader("歷史抽籤結果")

        # 合併所有歷史紀錄
        all_history = st.session_state.respites_history + st.session_state.shortterms_history
        
        # 顯示表格
        history_df = pd.DataFrame(all_history)
        if not history_df.empty:
            st.dataframe(history_df)

        # 顯示下拉選單來選擇具體的歷史紀錄
        selected_history = st.selectbox(
            "請選擇歷史抽籤結果", 
            [f"{record['單位名稱']} - {record['抽籤欄位']} (區域：{record['抽籤區域']}) (時間：{record['抽選時間']})" for record in all_history]
        )

        # 顯示選中的具體抽籤結果
        if selected_history:
            selected_record = next(
                record for record in all_history
                if f"{record['單位名稱']} - {record['抽籤欄位']} (區域：{record['抽籤區域']}) (時間：{record['抽選時間']})" == selected_history
            )
            st.write(f"選擇的抽籤結果：{selected_history}")
            st.dataframe(pd.DataFrame([selected_record]))  # 顯示該條歷史紀錄

else:
    st.info("請先上傳 Excel 檔案。")

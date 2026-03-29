import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 頁面配置
st.set_page_config(page_title="龍蝦特助 - 三角洲 & 代儲數據門戶", layout="wide")

# 初始化數據 (模擬數據)
data_path = "finance/delta_ledger_2026.csv"
if not os.path.exists("finance"):
    os.makedirs("finance")

if not os.path.exists(data_path):
    df = pd.DataFrame(columns=["日期", "打手ID", "項目", "單價", "成本", "利潤", "狀態"])
    df.to_csv(data_path, index=False, encoding='utf-8-sig')

# 模擬幾筆數據展示
sample_data = {
    "日期": ["2026-03-29", "2026-03-29", "2026-03-29"],
    "打手ID": ["打手A", "打手B", "打手A"],
    "項目": ["三角洲-航天場", "代儲-648", "護航-絕密"],
    "單價": [880, 2450, 500],
    "成本": [700, 2100, 350],
    "利潤": [180, 350, 150],
    "狀態": ["已結算", "待結算", "已結算"]
}
df_display = pd.DataFrame(sample_data)

# 側邊欄：新增訂單
with st.sidebar:
    st.header("🦞 快速報單")
    with st.form("order_form"):
        date = st.date_input("日期", datetime.now())
        player_id = st.text_input("打手 ID")
        item = st.selectbox("項目", ["三角洲-航天場", "護航-絕密", "代儲-648", "其他"])
        price = st.number_input("售價 (老闆)", min_value=0)
        cost = st.number_input("成本 (打手薪資)", min_value=0)
        status = st.radio("結算狀態", ["待結算", "已結算"])
        submit = st.form_submit_button("提交報單")
        if submit:
            st.success(f"已記錄：{player_id} - {item}")

# 主介面
st.title("🦞 龍蝦特助 - 數據管理門戶 (v1.0-Alpha)")

# 關鍵指標
col1, col2, col3, col4 = st.columns(4)
col1.metric("今日總營收", "NT$ 3,830", "15%")
col2.metric("今日總利潤", "NT$ 680", "12%")
col3.metric("待結算訂單", "1", "-1")
col4.metric("活躍打手數", "2", "0")

# 數據表格
st.subheader("📊 訂單明細")
st.dataframe(df_display, use_container_width=True)

# 簡單圖表
st.subheader("📈 利潤趨勢 (模擬)")
st.line_chart(df_display.set_index("日期")["利潤"])

st.info("💡 這是試作介面，稍後我會將其部署到您的本地環境，您可以直接透過瀏覽器開啟。")

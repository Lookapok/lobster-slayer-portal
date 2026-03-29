import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 頁面配置
st.set_page_config(page_title="小希｜三角洲撤離大師 - 管理門戶", layout="wide")

# 模擬數據路徑 (之後對接 Google Sheet)
# Sheet ID: 1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE
SHEET_ID = "1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE"

# 自定義 CSS (複刻截圖風格)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .status-tag {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-success { background-color: #d4edda; color: #155724; }
    .status-unsettled { background-color: #f8d7da; color: #721c24; }
    </style>
    """, unsafe_allow_html=True)

# 標題
st.title("🛡️ 小希｜三角洲撤離大師 - 管理門戶")

# 頂部指標
col1, col2, col3, col4 = st.columns(4)
col1.metric("今日總利潤", "NT$ 2,450", "+12%")
col2.metric("到手薪資總金額", "NT$ 18,300", "本月累計")
col3.metric("當前未結算工資", "NT$ 4,200", delta_color="inverse")
col4.metric("待處理單量", "5 筆", "-2")

# 側邊欄：進階搜尋與報單
with st.sidebar:
    st.image("https://via.placeholder.com/150?text=Lobster", width=100) # 暫代頭像
    st.header("⚙️ 管理選單")
    st.subheader("快速報單")
    with st.form("order_form"):
        player = st.selectbox("打手 ID", ["打手A (90%)", "打手B (80%)", "打手C (90%)"])
        customer_id = st.text_input("老闆 ID")
        item = st.selectbox("項目", ["三角洲-航天場", "三角洲-絕密", "代儲-648", "代儲-328"])
        price = st.number_input("售價 (老闆)", min_value=0)
        discount = st.number_input("折扣", min_value=0)
        
        # 自動計算邏輯 (基於老大提供的 90%/80% 規則)
        rate = 0.9 if "90%" in player else 0.8
        net_price = price - discount
        settle_amount = int(net_price * rate)
        profit = net_price - settle_amount
        
        st.write(f"📊 預估結算: NT$ {settle_amount}")
        st.write(f"💰 預估利潤: NT$ {profit}")
        
        submit = st.form_submit_button("確認提交至 Google Sheet")
        if submit:
            st.success("已同步至試算表！")

# 訂單明細清單 (複刻截圖風格)
st.subheader("📅 訂單明細清單")

# 模擬清單數據
data = {
    "日期": ["2026-03-29", "2026-03-29", "2026-03-28", "2026-03-28", "2026-03-28"],
    "陪玩ID": ["打手A", "打手B", "打手A", "打手C", "打手B"],
    "派單客服": ["DK", "客服01", "DK", "DK", "客服01"],
    "接單狀態": ["審核通過", "審核通過", "審核通過", "審核通過", "審核通過"],
    "結算狀態": ["已結算", "待結算", "已結算", "待結算", "待結算"],
    "遊戲名稱": ["三角洲行動", "三角洲行動", "代儲服務", "三角洲行動", "代儲服務"],
    "項目": ["航天場護航", "絕密場護航", "648 金幣", "航天場護航", "328 金幣"],
    "單價": [880, 500, 2450, 880, 1250],
    "折扣": [0, 50, 100, 0, 0],
    "結算": [792, 360, 2115, 792, 1000]
}
df = pd.DataFrame(data)

# 使用表格顯示
st.dataframe(df.style.map(lambda x: "color: green" if x == "已結算" else ("color: red" if x == "待結算" else ""), subset=["結算狀態"]), use_container_width=True)

st.divider()
st.caption("龍蝦特助 (Lobster) 🦞 - 2026 傑斯工作室 版權所有")

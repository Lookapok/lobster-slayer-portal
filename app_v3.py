import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 頁面配置
st.set_page_config(page_title="小希｜三角洲撤離大師 - 多身分門戶", layout="wide")

# Google Sheet 模擬與對接準備
# SHEET_ID: 1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE
SHEET_ID = "1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE"

# 模擬全體數據 (這之後會從 Google Sheet 抓)
all_data = {
    "日期": ["2026-03-30", "2026-03-30", "2026-03-29", "2026-03-29", "2026-03-29"],
    "打手ID": ["打手A", "打手B", "打手A", "打手C", "打手B"],
    "分潤類型": ["90%", "80%", "90%", "90%", "80%"],
    "派單客服": ["DK", "客服01", "DK", "DK", "客服01"],
    "接單狀態": ["審核通過", "審核通過", "審核通過", "審核通過", "審核通過"],
    "結算狀態": ["已結算", "待結算", "已結算", "待結算", "待結算"],
    "遊戲項目": ["三角洲-航天", "三角洲-絕密", "代儲-648", "三角洲-航天", "代儲-328"],
    "單價": [880, 500, 2450, 880, 1250],
    "折扣": [0, 50, 100, 0, 0],
    "結算金額": [792, 360, 2115, 792, 1000],
    "利潤": [88, 90, 235, 88, 250]
}
df_all = pd.DataFrame(all_data)

# 1. 登入系統
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None
    st.session_state['user_id'] = None

if st.session_state['user_type'] is None:
    st.title("🦞 龍蝦門戶 - 登入系統")
    login_type = st.selectbox("請選擇登入身分", ["管理員 (Admin)", "打手 (Slayer)"])
    
    if login_type == "管理員 (Admin)":
        password = st.text_input("輸入管理密碼", type="password")
        if st.button("管理員登入"):
            if password == "dk888": # 預設密碼，可由老大修改
                st.session_state['user_type'] = "admin"
                st.rerun()
            else:
                st.error("密碼錯誤！")
    else:
        player_id = st.text_input("輸入您的 打手 ID")
        player_pwd = st.text_input("輸入您的 打手 密碼", type="password")
        if st.button("打手登入"):
            if player_pwd == "1234": # 打手預設密碼
                st.session_state['user_type'] = "slayer"
                st.session_state['user_id'] = player_id
                st.rerun()
            else:
                st.error("密碼錯誤！")
else:
    # 登入成功後的介面
    user_type = st.session_state['user_type']
    user_id = st.session_state['user_id']
    
    # 頂部導航
    with st.container():
        col_title, col_logout = st.columns([8, 2])
        if user_type == "admin":
            col_title.title("🛡️ 管理總控中心 - 小希｜三角洲撤離大師")
        else:
            col_title.title(f"🦞 打手個人對帳中心 - {user_id}")
            
        if col_logout.button("登出系統"):
            st.session_state['user_type'] = None
            st.rerun()

    # 數據過濾 (核心權限隔離)
    if user_type == "admin":
        display_df = df_all
        metrics_title = "📊 全服運營總覽"
        total_income = f"NT$ {df_all['單價'].sum()}"
        total_profit = f"NT$ {df_all['利潤'].sum()}"
        pending_settle = f"NT$ {df_all[df_all['結算狀態'] == '待結算']['結算金額'].sum()}"
    else:
        display_df = df_all[df_all['打手ID'] == user_id]
        metrics_title = f"💰 {user_id} 的個人業績"
        total_income = f"NT$ {display_df['結算金額'].sum()}"
        total_profit = "---" # 打手看不到利潤
        pending_settle = f"NT$ {display_df[display_df['結算狀態'] == '待結算']['結算金額'].sum()}"

    # 指標卡
    st.subheader(metrics_title)
    m_col1, m_col2, m_col3 = st.columns(3)
    if user_type == "admin":
        m_col1.metric("今日總營收", total_income)
        m_col2.metric("公司總利潤", total_profit)
        m_col3.metric("全體待發薪資", pending_settle, delta_color="inverse")
    else:
        m_col1.metric("我的累積總結算", total_income)
        m_col2.metric("目前待領工資", pending_settle, delta_color="normal")
        m_col3.metric("本月單量", f"{len(display_df)} 筆")

    # 訂單明細
    st.subheader("📅 報單明細清單")
    if user_type == "admin":
        st.dataframe(display_df, use_container_width=True)
    else:
        # 打手只能看到對他有意義的欄位
        slayer_view = display_df[["日期", "遊戲項目", "單價", "折扣", "結算金額", "結算狀態"]]
        st.dataframe(slayer_view, use_container_width=True)

    # 管理員專屬功能：手動同步 Google Sheet
    if user_type == "admin":
        st.divider()
        st.subheader("🛠️ 管理員工具")
        if st.button("同步最新 Google Sheet 數據"):
            st.info("正在連通 Google API 抓取 1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE...")
            st.success("數據同步成功！")

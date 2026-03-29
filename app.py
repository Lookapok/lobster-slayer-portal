import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 頁面配置
st.set_page_config(page_title="小希｜三角洲撤離大師 - 智能報單系統", layout="wide")

# 配置區域
STAFF_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1135665106"
ORDERS_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1411132681"
GAS_URL = "https://script.google.com/macros/s/AKfycbz2BdC_RM2iq6xVSzZfT1dHMPmGH7r_pG9OdBo9wtHPkJMac6z539ERT4q4g7LB5l4/exec"

# 項目數據庫 (與老大提供的價格對齊)
ITEMS_DATA = {
    "台服-體驗單($300/300W)": 300,
    "台服-基礎保底($500/588W)": 500,
    "台服-進階保底($1,000/1,088W)": 1000,
    "台服-計時護航($800/小時)": 800,
    "台服-航天計時($1,000/小時)": 1000,
    "台服-航天基礎($1,200/788W)": 1200,
    "台服-航天進階($2,600/1,688W)": 2600,
    "陸服-體驗單($350/300W)": 350,
    "陸服-基礎保底($600/588W)": 600,
    "陸服-進階保底($1,200/1,088W)": 1200,
    "陸服-計時護航($1,000/小時)": 1000,
    "陸服-航天計時($1,200/小時)": 1200,
    "陸服-航天基礎($1,400/788W)": 1400,
    "陸服-航天進階($2,800/1,688W)": 2800,
    "自定義項目": 0
}

def get_staff_data():
    try:
        df = pd.read_csv(STAFF_URL)
        df.columns = df.columns.str.strip()
        for col in df.columns: df[col] = df[col].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

def get_orders_data():
    try:
        df = pd.read_csv(ORDERS_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

# 1. 登入系統
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None
    st.session_state['user_id'] = None
    st.session_state['user_rate'] = 0.8

if st.session_state['user_type'] is None:
    st.title("🦞 龍蝦門戶 - 登入系統")
    login_type = st.selectbox("請選擇登入身分", ["管理員 (Admin)", "打手 (Slayer)"])
    
    if login_type == "管理員 (Admin)":
        password = st.text_input("輸入管理密碼", type="password")
        if st.button("管理員登入"):
            if password == "dk888":
                st.session_state['user_type'] = "admin"
                st.rerun()
            else:
                st.error("密碼錯誤！")
    else:
        player_id = st.text_input("輸入您的 打手 ID")
        player_pwd = st.text_input("輸入您的 打手 密碼", type="password")
        if st.button("打手登入"):
            staff_df = get_staff_data()
            if not staff_df.empty and player_id.strip() in staff_df['打手ID'].values:
                player_info = staff_df[staff_df['打手ID'] == player_id.strip()].iloc[0]
                if str(player_pwd).strip() == str(player_info.get('登入密碼', '1234')):
                    st.session_state['user_type'] = "slayer"
                    st.session_state['user_id'] = player_id.strip()
                    rate_col = [c for c in staff_df.columns if '比例' in c][0]
                    st.session_state['user_rate'] = float(player_info[rate_col])
                    st.rerun()
                else: st.error("密碼錯誤！")
            else: st.error("找不到該打手 ID")
else:
    user_type = st.session_state['user_type']
    user_id = st.session_state['user_id']
    user_rate = st.session_state['user_rate']
    
    with st.container():
        col_t, col_l = st.columns([8, 2])
        col_t.title(f"🛡️ {'管理中心' if user_type == 'admin' else '打手對帳 - ' + user_id}")
        if col_l.button("登出"):
            st.session_state['user_type'] = None
            st.rerun()

    if user_type == "slayer":
        st.subheader("📝 提交新報單")
        with st.form("detailed_report", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            order_date = c1.date_input("日期", datetime.now())
            slayer_id = c2.text_input("打手 ID", value=user_id, disabled=True)
            rate_label = c3.text_input("分潤比例", value=f"{int(user_rate*100)}%", disabled=True)
            
            c4, c5, c5_time = st.columns([2, 3, 1])
            cust_id = c4.text_input("老闆 ID (必填)")
            item_selected = c5.selectbox("選擇護航項目", list(ITEMS_DATA.keys()))
            duration = c5_time.number_input("時數/次數", min_value=1, value=1)
            
            c6, c7, c8 = st.columns(3)
            base_price = ITEMS_DATA[item_selected]
            discount = c6.selectbox("折扣金額", [0, 50, 100, 150, 200, 300, 500])
            
            # --- 智能計算公式：(單價 * 時數) - 折扣 ---
            total_after_discount = (base_price * duration) - discount
            price_display = c7.number_input("最終成交價 (自動算好)", value=total_after_discount, disabled=True)
            
            # 結算與利潤
            cut = int(total_after_discount * user_rate)
            profit = total_after_discount - cut
            c8.metric("預估結算 (打手薪資)", f"NT$ {cut}")
            
            remark = st.text_area("備註")
            
            if st.form_submit_button("🚀 確認提交報單"):
                if not cust_id:
                    st.error("請填寫老闆 ID！")
                else:
                    payload = {
                        "date": order_date.strftime("%Y-%m-%d"),
                        "slayer_id": user_id,
                        "rate_type": f"{int(user_rate*100)}%",
                        "customer_id": cust_id,
                        "item": f"{item_selected} (x{duration})",
                        "price": total_after_discount,
                        "discount": discount,
                        "slayer_cut": cut,
                        "profit": profit
                    }
                    try:
                        resp = requests.post(GAS_URL, json=payload)
                        if resp.status_code == 200:
                            st.success(f"報單成功！薪資 NT$ {cut} 已計入。")
                            st.balloons()
                        else: st.error("同步失敗")
                    except: st.error("連連線異常")

        st.divider()
        st.subheader("📅 我的報單歷史")
        orders_df = get_orders_data()
        if not orders_df.empty and '打手ID' in orders_df.columns:
            st.dataframe(orders_df[orders_df['打手ID'].astype(str) == user_id], use_container_width=True)
    
    elif user_type == "admin":
        orders_df = get_orders_data()
        st.subheader("📊 全服數據監控")
        if not orders_df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("總營收", f"NT$ {orders_df['單價'].sum()}")
            m2.metric("總利潤", f"NT$ {orders_df['公司利潤'].sum()}")
            m3.metric("總單量", f"{len(orders_df)} 筆")
            st.dataframe(orders_df, use_container_width=True)
        if st.button("刷新數據"): st.rerun()

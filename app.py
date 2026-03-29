import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

# 頁面配置
st.set_page_config(page_title="小希｜三角洲撤離大師 - 階級自動化版", layout="wide")

# 配置區域
STAFF_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1135665106"
ORDERS_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1411132681"
GAS_URL = "https://script.google.com/macros/s/AKfycbz2BdC_RM2iq6xVSzZfT1dHMPmGH7r_pG9OdBo9wtHPkJMac6z539ERT4q4g7LB5l4/exec"

# 基礎價格定義 (普通打手)
BASE_PRICES = {
    "台服-體驗單": 300, "台服-基礎保底": 500, "台服-進階保底": 1000, "台服-計時護航": 800,
    "陸服-體驗單": 350, "陸服-基礎保底": 600, "陸服-進階保底": 1200, "陸服-計時護航": 1000,
    "自定義": 0
}

# 階級加乘或特定價格 (範例：魔王計時 1200, 巔峰計時 1500)
def get_dynamic_price(item, tier):
    base = BASE_PRICES.get(item, 0)
    if tier == "魔王":
        if "計時" in item: return 1200
        return base * 1.2 # 非計時單自動加成 20%
    elif tier == "巔峰":
        if "計時" in item: return 1500
        return base * 1.5 # 非計時單自動加成 50%
    return base

def get_staff_data():
    try:
        df = pd.read_csv(f"{STAFF_URL}&t={int(time.time())}")
        df.columns = df.columns.str.strip()
        for col in df.columns: df[col] = df[col].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

def get_orders_data():
    try:
        df = pd.read_csv(f"{ORDERS_URL}&t={int(time.time())}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

# 1. 登入系統
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None

if st.session_state['user_type'] is None:
    st.title("🦞 龍蝦門戶 - 階級系統")
    login_type = st.selectbox("身分", ["管理員 (Admin)", "打手 (Slayer)"])
    if login_type == "管理員 (Admin)":
        password = st.text_input("密碼", type="password")
        if st.button("登入"):
            if password == "dk888": st.session_state['user_type'] = "admin"; st.rerun()
    else:
        player_id = st.text_input("打手 ID")
        player_pwd = st.text_input("密碼", type="password")
        if st.button("登入"):
            staff_df = get_staff_data()
            if not staff_df.empty and player_id.strip() in staff_df['打手ID'].values:
                user_row = staff_df[staff_df['打手ID'] == player_id.strip()].iloc[0]
                rate_col = [c for c in staff_df.columns if '比例' in c][0]
                # 獲取階級，若無則預設為「普通」
                tier = user_row.get('階級', '普通')
                st.session_state['user_type'] = "slayer"
                st.session_state['user_id'] = player_id.strip()
                st.session_state['user_rate'] = float(user_row[rate_col])
                st.session_state['user_tier'] = tier
                st.rerun()
            else: st.error("找不到該打手 ID")
else:
    user_type = st.session_state['user_type']
    if st.sidebar.button("登出"): st.session_state['user_type'] = None; st.rerun()

    if user_type == "slayer":
        tier = st.session_state['user_tier']
        st.title(f"🛡️ {tier}級打手 - {st.session_state['user_id']}")
        
        # 報單表單
        c1, c2, c3 = st.columns([2, 4, 1])
        cust_id = c1.text_input("老闆 ID")
        item = c2.selectbox("項目", list(BASE_PRICES.keys()))
        dur = c3.number_input("時數", min_value=1, value=1)
        disc = st.selectbox("折扣", [0, 50, 100, 150, 200, 300])
        
        # --- 自動識別階級訂價 ---
        unit_price = get_dynamic_price(item, tier)
        total_price = (unit_price * dur) - disc
        user_cut = int(total_price * st.session_state['user_rate'])
        
        st.info(f"您的階級：{tier} | 當前單價：${unit_price}")
        st.markdown(f"### 最終成交價: {total_price} | 您的結算: {user_cut}")
        
        if st.button("🚀 確認提交"):
            payload = {"date": datetime.now().strftime("%Y-%m-%d"), "slayer_id": st.session_state['user_id'], "rate_type": f"{tier}({int(st.session_state['user_rate']*100)}%)", "customer_id": cust_id, "item": f"{item}({tier}) x{dur}", "price": total_price, "discount": disc, "slayer_cut": user_cut, "profit": total_price - user_cut}
            requests.post(GAS_URL, json=payload); st.success("報單成功！"); st.balloons(); time.sleep(1.5); st.rerun()

        st.divider(); st.subheader("歷史紀錄"); ord_df = get_orders_data()
        if not ord_df.empty:
            my_df = ord_df[ord_df['打手ID'].astype(str)==st.session_state['user_id']]
            st.dataframe(my_df[[c for c in my_df.columns if c != "分潤類型"]], use_container_width=True)

    elif user_type == "admin":
        st.title("🛡️ 老闆總控後台")
        df = get_orders_data()
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("今日營收", f"${int(pd.to_numeric(df['單價'], errors='coerce').sum())}")
            m2.metric("總利潤", f"${int(pd.to_numeric(df['公司利潤'], errors='coerce').sum())}")
            m3.metric("總單量", f"{len(df)} 筆")
            st.dataframe(df, use_container_width=True)

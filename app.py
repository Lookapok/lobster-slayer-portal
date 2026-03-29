import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# 頁面配置 (鎖定黃金格式)
st.set_page_config(page_title="小希｜三角洲撤離大師 - 專業報單門戶", layout="wide")

# 配置區域
STAFF_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1135665106"
ORDERS_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1411132681"
GAS_URL = "https://script.google.com/macros/s/AKfycbz2BdC_RM2iq6xVSzZfT1dHMPmGH7r_pG9OdBo9wtHPkJMac6z539ERT4q4g7LB5l4/exec"

# 項目數據庫
ITEMS_DATA = {
    "台服-體驗單($300/300W)": 300, "台服-基礎保底($500/588W)": 500, "台服-進階保底($1,000/1,088W)": 1000,
    "台服-計時護航($800/小時)": 800, "台服-航天計時($1,000/小時)": 1000, "台服-航天基礎($1,200/788W)": 1200,
    "台服-航天進階($2,600/1,688W)": 2600, "陸服-體驗單($350/300W)": 350, "陸服-基礎保底($600/588W)": 600,
    "陸服-進階保底($1,200/1,088W)": 1200, "陸服-計時護航($1,000/小時)": 1000, "陸服-航天計時($1,200/小時)": 1200,
    "陸服-航天基礎($1,400/788W)": 1400, "陸服-航天進階($2,800/1,688W)": 2800, "自定義項目": 0
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

# 登入邏輯
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None

if st.session_state['user_type'] is None:
    st.title("🦞 龍蝦門戶 - 登入系統")
    login_type = st.selectbox("身分", ["管理員 (Admin)", "打手 (Slayer)"])
    if login_type == "管理員 (Admin)":
        pwd_i = st.text_input("密碼", type="password")
        if st.button("登入"):
            if pwd_i == "dk888": st.session_state['user_type'] = "admin"; st.rerun()
    else:
        pid = st.text_input("打手 ID")
        pwd = st.text_input("密碼", type="password")
        if st.button("登入"):
            staff_df = get_staff_data()
            if pid in staff_df['打手ID'].astype(str).values:
                user_row = staff_df[staff_df['打手ID'].astype(str) == pid].iloc[0]
                rate_col = [c for c in staff_df.columns if '比例' in c][0]
                st.session_state['user_type'] = "slayer"; st.session_state['user_id'] = pid
                st.session_state['user_rate'] = float(user_row[rate_col])
                st.rerun()
            else: st.error("找不到該打手 ID")
else:
    user_type = st.session_state['user_type']
    if st.sidebar.button("登出"): st.session_state['user_type'] = None; st.rerun()

    if user_type == "slayer":
        st.title(f"🛡️ 打手到帳 - {st.session_state['user_id']}")
        st.subheader("📝 提交新報單")
        with st.container():
            r1c1, r1c2, r1c3 = st.columns(3)
            r1c1.text_input("日期", value=datetime.now().strftime("%Y/%m/%d"), disabled=True)
            r1c2.text_input("打手 ID", value=st.session_state['user_id'], disabled=True)
            r1c3.text_input("分潤比例", value=f"{int(st.session_state['user_rate']*100)}%", disabled=True)
            r2c1, r2c2, r2c3 = st.columns([2, 4, 1])
            cust_id = r2c1.text_input("老闆 ID (必填)")
            item = r2c2.selectbox("選擇護航項目", list(ITEMS_DATA.keys()))
            dur = r2c3.number_input("時數/次數", min_value=1, value=1)
            r3c1, r3c2, r3c3 = st.columns(3)
            disc = r3c1.selectbox("折扣金額", [0, 50, 100, 150, 200, 300, 500])
            total_price = (ITEMS_DATA[item] * dur) - disc
            r3c2.number_input("最終成交價 (自動算好)", value=total_price, disabled=True)
            user_cut = int(total_price * st.session_state['user_rate'])
            r3c3.write("預估結算 (打手薪資)")
            r3c3.subheader(f"NT$ {user_cut}")
            remark = st.text_area("備註")
            if st.button("🚀 確認提交報單"):
                if not cust_id: st.error("請填寫老闆 ID")
                else:
                    payload = {"date": datetime.now().strftime("%Y-%m-%d"), "slayer_id": st.session_state['user_id'], "rate_type": f"{int(st.session_state['user_rate']*100)}%", "customer_id": cust_id, "item": f"{item} (x{dur})", "price": total_price, "discount": disc, "slayer_cut": user_cut, "profit": total_price - user_cut}
                    try: requests.post(GAS_URL, json=payload); st.success("報單成功！"); st.balloons()
                    except: st.error("同步失敗")
        st.divider(); st.subheader("📅 我的報單歷史"); ord_df = get_orders_data()
        if not ord_df.empty: st.dataframe(ord_df[ord_df['打手ID'].astype(str)==st.session_state['user_id']], use_container_width=True)

    elif user_type == "admin":
        st.title("🛡️ 老闆總控後台")
        df = get_orders_data()
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("今日總利潤", f"${df['公司利潤'].sum()}")
            m2.metric("待結算單數", len(df[df['結算狀態']=='待結算']))
            m3.metric("總單量", len(df))
            st.subheader("💸 發薪審核")
            pending = df[df['結算狀態'] == '待結算']
            for idx, row in pending.iterrows():
                col1, col2 = st.columns([8, 2])
                col1.write(f"📅 {row['日期']} | 👤 {row['打手ID']} | 💰 ${row['結算金額']} ({row['項目']})")
                if col2.button(f"✅ 發薪", key=f"p_{idx}"):
                    # 修正這裡：使用正確的欄位名稱（中文）
                    payload = {"action": "update_status", "date": row['日期'], "slayer_id": str(row['打手ID']), "customer_id": str(row['老闆ID']), "new_status": "已結算"}
                    requests.post(GAS_URL, json=payload); st.rerun()
            st.divider(); st.subheader("歷史紀錄"); st.dataframe(df, use_container_width=True)

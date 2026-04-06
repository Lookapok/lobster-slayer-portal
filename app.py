import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

# 頁面配置
st.set_page_config(page_title="小希｜三角洲撤離大師 - 智能連動門戶", layout="wide")

# 配置區域
STAFF_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1135665106"
ORDERS_URL = "https://docs.google.com/spreadsheets/d/1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE/export?format=csv&gid=1411132681"
GAS_URL = "https://script.google.com/macros/s/AKfycbz2BdC_RM2iq6xVSzZfT1dHMPmGH7r_pG9OdBo9wtHPkJMac6z539ERT4q4g7LB5l4/exec"

# --- 智能項目數據結構 ---
PRICING_DATA = {
    "體驗單": {
        "台服": {
            "體驗單：$400 (788W)": 400,
            "體驗單：$1,000 (1,488W)": 1000
        },
        "陸服": {
            "體驗單：$350 (300W)": 350,
            "體驗單：$600 (588W)": 600,
            "體驗單：$1,200 (1,088W)": 1200
        }
    },
    "護航單": {
        "常規": {
            "台服-計時 ($800)": 800,
            "陸服-計時 ($1,000)": 1000
        },
        "機密": {
            "台服-計時 ($800)": 800,
            "台服-基礎保底 ($800)": 800,
            "陸服-計時 ($1,000)": 1000,
            "陸服-基礎保底 ($1,000)": 1000
        },
        "絕密": {
            "台服-計時 ($1,000)": 1000,
            "台服-基礎保底 ($1,200)": 1200,
            "台服-進階保底 ($2,600)": 2600,
            "陸服-計時 ($1,200)": 1200,
            "陸服-基礎保底 ($1,400)": 1400,
            "陸服-進階保底 ($2,800)": 2800
        }
    },
    "趣味單": {
        "活動預留": {
            "趣味單項目A (預留)": 0,
            "趣味單項目B (預留)": 0
        }
    },
    "自定義單": {
        "手動輸入": {
            "自定義報價單": 0
        }
    }
}

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
    st.title("🦞 龍蝦門戶 - 智能系統")
    login_type = st.selectbox("請選擇登入身分", ["管理員 (Admin)", "打手 (Slayer)"])
    if login_type == "管理員 (Admin)":
        password = st.text_input("輸入管理密碼", type="password")
        if st.button("登入"):
            if password == "dk888": st.session_state['user_type'] = "admin"; st.rerun()
            else: st.error("密碼錯誤！")
    else:
        player_id = st.text_input("輸入您的 打手 ID")
        player_pwd = st.text_input("輸入您的 打手 密碼", type="password")
        if st.button("打手登入"):
            staff_df = get_staff_data()
            if not staff_df.empty and player_id.strip() in staff_df['打手ID'].values:
                user_row = staff_df[staff_df['打手ID'] == player_id.strip()].iloc[0]
                rate_col = [c for c in staff_df.columns if '比例' in c][0]
                tier_col = [c for c in staff_df.columns if '階級' in c]
                tier = user_row[tier_col[0]] if tier_col else "普通"
                if str(player_pwd).strip() == str(user_row.get('登入密碼', '1234')):
                    st.session_state['user_type'] = "slayer"; st.session_state['user_id'] = player_id.strip()
                    st.session_state['user_rate'] = float(user_row[rate_col]); st.session_state['user_tier'] = tier
                    st.rerun()
                else: st.error("密碼錯誤！")
            else: st.error("找不到該打手 ID")
else:
    user_type = st.session_state['user_type']
    if st.sidebar.button("登出系統"): st.session_state['user_type'] = None; st.rerun()

    if user_type == "slayer":
        st.title(f"🛡️ 打手對帳中心 - {st.session_state['user_id']}")
        st.subheader("📝 提交新報單")
        
        with st.container():
            r1c1, r1c2 = st.columns(2)
            r1c1.text_input("日期", value=datetime.now().strftime("%Y/%m/%d"), disabled=True)
            r1c2.text_input("打手 ID", value=st.session_state['user_id'], disabled=True)
            
            # --- 分類選擇邏輯 ---
            r2c1, r2c2, r2c3, r2c4 = st.columns([2, 2, 2, 3])
            cust_id = r2c1.text_input("老闆 ID (必填)")
            type_lvl1 = r2c2.selectbox("單量類型", ["體驗單", "護航單", "趣味單", "自定義單"])
            
            if type_lvl1 == "體驗單":
                region = r2c3.selectbox("區域", ["台服", "陸服"])
                item_options = PRICING_DATA["體驗單"][region]
            elif type_lvl1 == "護航單":
                map_lvl = r2c3.selectbox("地圖等級", ["常規", "機密", "絕密"])
                item_options = PRICING_DATA["護航單"][map_lvl]
            elif type_lvl1 == "趣味單":
                st.info("💡 趣味單模式預留中...")
                item_options = PRICING_DATA["趣味單"]["活動預留"]
            else:
                r2c3.write("自行填寫金額")
                item_options = PRICING_DATA["自定義單"]["手動輸入"]
            
            item_name = r2c4.selectbox("護航項目", list(item_options.keys()))
            
            # --- 金額計算邏輯 ---
            r3c1, r3c2, r3c3, r3c4 = st.columns([1, 2, 2, 2])
            dur = r3c1.number_input("時數/次數", min_value=1, value=1)
            
            # 如果是自定義單或趣味單，開放單價輸入；否則自動帶入
            if type_lvl1 in ["自定義單", "趣味單"]:
                base_p = r3c2.number_input("單價 (手動填寫)", min_value=0, value=0)
                disc = r3c3.selectbox("折扣金額", [0, 50, 100, 150, 200, 300, 500])
            else:
                base_p = item_options[item_name]
                # 階級加乘邏輯
                tier = st.session_state.get('user_tier', '普通')
                if "計時" in item_name:
                    if tier == "魔王": base_p = 1200 if "台服" in item_name or "常規" in item_name else 1500
                    elif tier == "巔峰": base_p = 1500 if "台服" in item_name or "常規" in item_name else 1800
                disc = r3c2.selectbox("折扣金額", [0, 50, 100, 150, 200, 300, 500])
            
            # 核心公式：單價 * 時數 - 折扣
            total_price = (base_p * dur) - disc
            # 雙人護航邏輯：單人薪資 = (總金額 * 分潤比例) / 2
            user_cut = int((total_price * st.session_state['user_rate']) / 2)
            
            if type_lvl1 in ["自定義單", "趣味單"]:
                r3c4.metric("單人薪資 (一人一半)", f"NT$ {user_cut}")
            else:
                r3c3.number_input("最終成交總價", value=total_price, disabled=True)
                r3c4.metric("單人薪資 (一人一半)", f"NT$ {user_cut}")
            
            remark = st.text_area("備註")
            
            if st.button("🚀 確認提交報單"):
                if not cust_id: st.error("請填寫老闆 ID")
                else:
                    payload = {"date": datetime.now().strftime("%Y-%m-%d"), "slayer_id": st.session_state['user_id'], "rate_type": f"{st.session_state.get('user_tier', '普通')}({int(st.session_state['user_rate']*100)}%)", "customer_id": cust_id, "item": f"{item_name} x{dur}", "price": total_price, "discount": disc, "slayer_cut": user_cut, "profit": total_price - (user_cut * 2)}
                    try: requests.post(GAS_URL, json=payload, timeout=15); st.success("報單成功！"); st.balloons(); time.sleep(1.5); st.rerun()
                    except: st.error("同步失敗")

        st.divider(); st.subheader("📅 我的報單歷史紀錄"); ord_df = get_orders_data()
        if not ord_df.empty:
            my_df = ord_df[ord_df['打手ID'].astype(str)==st.session_state['user_id']]
            st.dataframe(my_df[[c for c in my_df.columns if c != "分潤類型"]], use_container_width=True)

    elif user_type == "admin":
        st.title("🛡️ 老闆總控後台")
        df = get_orders_data()
        if not df.empty:
            df['單價'] = pd.to_numeric(df['單價'], errors='coerce').fillna(0)
            df['公司利潤'] = pd.to_numeric(df['公司利潤'], errors='coerce').fillna(0)
            m1, m2, m3 = st.columns(3)
            m1.metric("今日總營收", f"${int(df['單價'].sum())}")
            m2.metric("總利潤", f"${int(df['公司利潤'].sum())}")
            m3.metric("總單量", len(df))
            st.dataframe(df, use_container_width=True)

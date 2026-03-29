import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 頁面配置
st.set_page_config(page_title="小希｜三角洲撤離大師 - 多身分門戶 v3.1", layout="wide")

# Google Sheet 數據對接準備
SHEET_ID = "1zbJKbDKVg4qX1pCjQn0zr5WSfpFk2NQtRlzpZ7OAarE"

# 模擬全體數據 (之後對接 Google Sheet)
if 'df_orders' not in st.session_state:
    st.session_state['df_orders'] = pd.DataFrame(columns=[
        "日期", "打手ID", "分潤類型", "老闆ID", "派單客服", "接單狀態", "結算狀態", "遊戲名稱", "項目", "單價", "折扣", "結算金額", "公司利潤", "備註"
    ])

# 1. 登入系統
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None
    st.session_state['user_id'] = None
    st.session_state['user_rate'] = 0.9

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
            if player_pwd == "1234":
                st.session_state['user_type'] = "slayer"
                st.session_state['user_id'] = player_id
                # 模擬獲取打手分潤 (打手A 90%, 其他 80%)
                st.session_state['user_rate'] = 0.9 if player_id == "打手A" else 0.8
                st.rerun()
            else:
                st.error("密碼錯誤！")
else:
    user_type = st.session_state['user_type']
    user_id = st.session_state['user_id']
    user_rate = st.session_state['user_rate']
    
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

    # --- 打手報單頁面 (完全複刻截圖) ---
    if user_type == "slayer":
        st.subheader("📝 提交新報單")
        with st.expander("點擊展開報單表單", expanded=True):
            with st.form("slayer_order_form"):
                col1, col2, col3 = st.columns(3)
                order_date = col1.date_input("日期", datetime.now())
                order_time = col2.time_input("時間", datetime.now().time())
                slayer_id_fixed = col3.text_input("陪玩 ID", value=user_id, disabled=True)
                
                col4, col5, col6 = st.columns(3)
                customer_id = col4.text_input("老闆 ID (必填)")
                staff_name = col5.selectbox("派單客服", ["DK", "客服01", "客服02"])
                order_status = col6.selectbox("接單狀態", ["服務完成", "審核通過"])
                
                col7, col8, col9 = st.columns(3)
                settle_status = col7.text_input("結算狀態", value="未結算", disabled=True)
                game_name = col8.selectbox("遊戲名稱", ["三角洲行動", "特戰英豪", "王者榮耀", "代儲服務"])
                item_tag = col9.selectbox("項目 TAG", ["航天護航", "絕密護航", "648 金幣", "328 金幣", "陪玩/帶飛"])
                
                col10, col11, col12 = st.columns(3)
                price = col10.number_input("單價 (售價)", min_value=0)
                discount = col11.number_input("折扣", min_value=0)
                
                # 自動計算預覽
                net_price = price - discount
                slayer_cut = int(net_price * user_rate)
                profit = net_price - slayer_cut
                col12.info(f"💰 預估結算: {slayer_cut}")
                
                remark = st.text_area("備註 (老闆需求/特殊情況)")
                
                submit_order = st.form_submit_button("🚀 確認報單並同步至 Google Sheet")
                
                if submit_order:
                    new_order = {
                        "日期": order_date.strftime("%Y-%m-%d"),
                        "打手ID": user_id,
                        "分潤類型": f"{int(user_rate*100)}%",
                        "老闆ID": customer_id,
                        "派單客服": staff_name,
                        "接單狀態": order_status,
                        "結算狀態": "待結算",
                        "遊戲名稱": game_name,
                        "項目": item_tag,
                        "單價": price,
                        "折扣": discount,
                        "結算金額": slayer_cut,
                        "公司利潤": profit,
                        "備註": remark
                    }
                    st.session_state['df_orders'] = pd.concat([st.session_state['df_orders'], pd.DataFrame([new_order])], ignore_index=True)
                    st.success("報單成功！數據已存入暫存並準備同步至 Google Sheet。")

        # 打手查看自己的訂單
        st.subheader("📅 我的報單歷史")
        my_df = st.session_state['df_orders'][st.session_state['df_orders']['打手ID'] == user_id]
        st.dataframe(my_df[["日期", "遊戲名稱", "項目", "單價", "折扣", "結算金額", "結算狀態"]], use_container_width=True)

    # --- 管理員總覽介面 ---
    elif user_type == "admin":
        st.subheader("📊 全服數據總覽")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("今日總營收", f"NT$ {st.session_state['df_orders']['單價'].sum()}")
        m_col2.metric("累計總利潤", f"NT$ {st.session_state['df_orders']['公司利潤'].sum()}")
        m_col3.metric("全體待領薪資", f"NT$ {st.session_state['df_orders'][st.session_state['df_orders']['結算狀態'] == '待結算']['結算金額'].sum()}", delta_color="inverse")
        m_col4.metric("總單量", f"{len(st.session_state['df_orders'])} 筆")
        
        st.subheader("📋 所有訂單清單 (管理員專屬)")
        st.dataframe(st.session_state['df_orders'], use_container_width=True)
        
        # 簡單圖表
        if not st.session_state['df_orders'].empty:
            st.subheader("📈 利潤趨勢圖")
            st.line_chart(st.session_state['df_orders'].groupby("日期")["公司利潤"].sum())

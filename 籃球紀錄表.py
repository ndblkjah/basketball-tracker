import json
import pandas as pd
import streamlit as st


st.set_page_config(page_title="籃球換人紀錄系統", layout="wide")
st.title("🏀 專業換人數據紀錄台 (全功能版)")

# 1. 初始化全隊名單 (預設 12 人)
if 'roster' not in st.session_state:
    st.session_state.roster = {
        i: {"name": f"球員 {i+1}", "number": f"{i+1:02d}", "score": 0, "rebounds": 0, "assists": 0}
        for i in range(12)
    }

# 2. 定義更新函數
def update_stat(p_id, stat_key, delta):
    new_val = st.session_state.roster[p_id][stat_key] + delta
    if new_val >= 0:
        st.session_state.roster[p_id][stat_key] = new_val

# --- 側邊欄：全隊名單管理 ---
with st.sidebar:
    st.header("👥 全隊名單設定")
    for i in range(12):
        with st.expander(f"席位 {i+1}：{st.session_state.roster[i]['name']}"):
            st.session_state.roster[i]["name"] = st.text_input("姓名", value=st.session_state.roster[i]["name"], key=f"edit_n_{i}")
            st.session_state.roster[i]["number"] = st.text_input("背號", value=st.session_state.roster[i]["number"], key=f"edit_num_{i}")
    
    if st.button("🔄 全隊數據重置", type="primary"):
        for i in range(12):
            st.session_state.roster[i].update({"score": 0, "rebounds": 0, "assists": 0})
        st.rerun()

# --- 主畫面：即時紀錄與換人區 ---
st.subheader("🏃 場上球員紀錄 (請選擇目前上場的人員)")

# 建立 5 個紀錄位置
cols = st.columns(5)
# 準備選單選項清單
player_options = {i: f"#{st.session_state.roster[i]['number']} {st.session_state.roster[i]['name']}" for i in range(12)}

for slot in range(5):
    with cols[slot]:
        # 為了視覺區隔，我們可以用一個小容器框起來
        with st.container(border=True):
            st.write(f"**位置 {slot+1}**")
            # 下拉選單：選擇該位置目前是哪位球員
            selected_id = st.selectbox(
                "選擇球員",
                options=list(player_options.keys()),
                format_func=lambda x: player_options[x],
                key=f"slot_{slot}",
                label_visibility="collapsed" # 隱藏標籤讓畫面更乾淨
            )
            
            # 取得該球員目前的數據
            p = st.session_state.roster[selected_id]
            
            # 顯示當前球員的小型數據看板
            st.metric(label="得分", value=f"{p['score']} 分")
            st.write(f"🏀 R: {p['rebounds']} | 🤝 A: {p['assists']}")
            st.divider()
            
            # --- 得分操作區 ---
            st.write("**得分控制**")
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.button("➕ 加分", key=f"p_s_{slot}_{selected_id}", on_click=update_stat, args=(selected_id, "score", 1), use_container_width=True)
            with s_col2:
                st.button("➖ 修正", key=f"m_s_{slot}_{selected_id}", on_click=update_stat, args=(selected_id, "score", -1), use_container_width=True)
            
            # --- 籃板操作區 ---
            st.write("**籃板控制**")
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                if st.button("➕ 籃板", key=f"p_r_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "rebounds", 1); st.rerun()
            with r_col2:
                if st.button("➖ 修正", key=f"m_r_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "rebounds", -1); st.rerun()
                
            # --- 助攻操作區 ---
            st.write("**助攻控制**")
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                if st.button("➕ 助攻", key=f"p_a_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "assists", 1); st.rerun()
            with a_col2:
                if st.button("➖ 修正", key=f"m_a_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "assists", -1); st.rerun()

st.divider()

# --- 底部：匯出數據區 ---
st.subheader("💾 儲存與匯出比賽結果")

# 準備要匯出的乾淨數據
export_data = [
    {"背號": v["number"], "姓名": v["name"], "得分": v["score"], "籃板": v["rebounds"], "助攻": v["assists"]}
    for k, v in st.session_state.roster.items()
]

# 建立兩個按鈕並排
col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    # 匯出 JSON 格式 (適合軟體工程師或後續做資料庫分析)
    json_string = json.dumps(export_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 下載 JSON 檔",
        file_name="basketball_game_stats.json",
        mime="application/json",
        data=json_string,
        use_container_width=True
    )

with col_dl2:
    # 匯出 CSV 格式 (Excel 可以直接點開)
    # 注意：使用 'utf-8-sig' 可以避免中文在 Windows 的 Excel 打開時變成亂碼
    df = pd.DataFrame(export_data)
    csv = df.to_csv(index=False).encode('utf-8-sig') 
    st.download_button(
        label="📊 下載 Excel (CSV) 檔",
        file_name="basketball_game_stats.csv",
        mime="text/csv",
        data=csv,
        use_container_width=True
    )

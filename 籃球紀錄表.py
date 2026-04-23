import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="籃球換人紀錄系統", layout="wide")
st.title("🏀 專業換人數據紀錄台 (平板防鍵盤版)")

# 1. 初始化全隊名單 (預設 12 人)
if 'roster' not in st.session_state:
    st.session_state.roster = {
        i: {"name": f"球員 {i+1}", "number": f"{i+1:02d}", "score": 0, "rebounds": 0, "assists": 0}
        for i in range(12)
    }

# 2. 新增：初始化場上的 5 個位置 (預設為 ID 0 到 4 的球員先發)
if 'active_slots' not in st.session_state:
    st.session_state.active_slots = [0, 1, 2, 3, 4]

# 3. 定義更新函數
def update_stat(p_id, stat_key, delta):
    new_val = st.session_state.roster[p_id][stat_key] + delta
    if new_val >= 0:
        st.session_state.roster[p_id][stat_key] = new_val

def change_player(slot_index, new_player_id):
    """處理換人邏輯的函數"""
    st.session_state.active_slots[slot_index] = new_player_id

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

# --- 主畫面：橫式即時紀錄區 ---
st.subheader("🏃 場上球員紀錄")

player_options = {i: f"#{st.session_state.roster[i]['number']} {st.session_state.roster[i]['name']}" for i in range(12)}

header_cols = st.columns([2, 3, 3, 3])
header_cols[0].markdown("**場上球員 (點擊換人)**")
header_cols[1].markdown("**得分 (Score)**")
header_cols[2].markdown("**籃板 (Rebounds)**")
header_cols[3].markdown("**助攻 (Assists)**")

# 建立 5 個橫列
for slot in range(5):
    with st.container(border=True):
        cols = st.columns([2, 3, 3, 3])
        
        # --- 第一欄：彈出式換人選單 (取代 selectbox) ---
        with cols[0]:
            # 取得這個位置目前的球員 ID
            selected_id = st.session_state.active_slots[slot]
            p = st.session_state.roster[selected_id]
            
            # 使用 popover 製作彈出式面板
            with st.popover(f"🔄 {player_options[selected_id]}", use_container_width=True):
                st.markdown("**點擊替換上場球員：**")
                # 把 12 個球員排成兩排，按鈕比較大比較好按
                pop_cols = st.columns(2)
                for idx, (opt_id, opt_name) in enumerate(player_options.items()):
                    with pop_cols[idx % 2]:
                        if st.button(opt_name, key=f"btn_sub_{slot}_{opt_id}", use_container_width=True):
                            change_player(slot, opt_id)
                            st.rerun()
            
            # 顯示微縮數據
            st.caption(f"目前: {p['score']}分 | {p['rebounds']}板 | {p['assists']}助")
        
        # --- 第二欄：得分控制 ---
        with cols[1]:
            s_c1, s_c2 = st.columns(2)
            s_c1.button("➕ 加分", key=f"p_s_{slot}_{selected_id}", on_click=update_stat, args=(selected_id, "score", 1), use_container_width=True)
            s_c2.button("➖ 修正", key=f"m_s_{slot}_{selected_id}", on_click=update_stat, args=(selected_id, "score", -1), use_container_width=True)
        
        # --- 第三欄：籃板控制 ---
        with cols[2]:
            r_c1, r_c2 = st.columns(2)
            if r_c1.button("➕ 籃板", key=f"p_r_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "rebounds", 1); st.rerun()
            if r_c2.button("➖ 修正", key=f"m_r_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "rebounds", -1); st.rerun()
            
        # --- 第四欄：助攻控制 ---
        with cols[3]:
            a_c1, a_c2 = st.columns(2)
            if a_c1.button("➕ 助攻", key=f"p_a_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "assists", 1); st.rerun()
            if a_c2.button("➖ 修正", key=f"m_a_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "assists", -1); st.rerun()

st.divider()

# --- 底部：全隊成績表與匯出區 ---
#st.subheader("📈 全隊數據與匯出")

export_data = [
    {"背號": v["number"], "姓名": v["name"], "得分": v["score"], "籃板": v["rebounds"], "助攻": v["assists"]}
    for k, v in st.session_state.roster.items()
]

st.dataframe(export_data, use_container_width=True)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    json_string = json.dumps(export_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 下載 JSON 檔",
        file_name="basketball_game_stats.json",
        mime="application/json",
        data=json_string,
        use_container_width=True
    )
with col_dl2:
    df = pd.DataFrame(export_data)
    csv = df.to_csv(index=False).encode('utf-8-sig') 
    st.download_button(
        label="📊 下載 Excel (CSV) 檔",
        file_name="basketball_game_stats.csv",
        mime="text/csv",
        data=csv,
        use_container_width=True
    )

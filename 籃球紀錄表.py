import streamlit as st
import pandas as pd
import json

# 設定為寬螢幕模式
st.set_page_config(page_title="籃球換人紀錄系統", layout="wide")
st.title("🏀 專業換人數據紀錄台 (橫式平板專用版)")

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

# --- 主畫面：橫式即時紀錄區 ---
st.subheader("🏃 場上球員紀錄")

player_options = {i: f"#{st.session_state.roster[i]['number']} {st.session_state.roster[i]['name']}" for i in range(12)}

# 建立標題列，[2, 3, 3, 3] 代表欄位的寬度比例
header_cols = st.columns([2, 3, 3, 3])
header_cols[0].markdown("**選擇場上球員**")
header_cols[1].markdown("**得分 (Score)**")
header_cols[2].markdown("**籃板 (Rebounds)**")
header_cols[3].markdown("**助攻 (Assists)**")

# 建立 5 個橫列 (Rows)
for slot in range(5):
    with st.container(border=True): # 用框線把每一列包起來，視覺更清晰
        cols = st.columns([2, 3, 3, 3]) # 保持與標題列相同的寬度比例
        
        # 第一欄：下拉選單與目前數據預覽
        with cols[0]:
            selected_id = st.selectbox(
                "選擇球員",
                options=list(player_options.keys()),
                format_func=lambda x: player_options[x],
                key=f"slot_{slot}",
                label_visibility="collapsed"
            )
            p = st.session_state.roster[selected_id]
            st.caption(f"目前: {p['score']}分 | {p['rebounds']}板 | {p['assists']}助")
        
        # 第二欄：得分控制 (左右並排)
        with cols[1]:
            s_c1, s_c2 = st.columns(2)
            s_c1.button("➕ 加分", key=f"p_s_{slot}_{selected_id}", on_click=update_stat, args=(selected_id, "score", 1), use_container_width=True)
            s_c2.button("➖ 修正", key=f"m_s_{slot}_{selected_id}", on_click=update_stat, args=(selected_id, "score", -1), use_container_width=True)
        
        # 第三欄：籃板控制 (左右並排)
        with cols[2]:
            r_c1, r_c2 = st.columns(2)
            if r_c1.button("➕ 籃板", key=f"p_r_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "rebounds", 1); st.rerun()
            if r_c2.button("➖ 修正", key=f"m_r_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "rebounds", -1); st.rerun()
            
        # 第四欄：助攻控制 (左右並排)
        with cols[3]:
            a_c1, a_c2 = st.columns(2)
            if a_c1.button("➕ 助攻", key=f"p_a_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "assists", 1); st.rerun()
            if a_c2.button("➖ 修正", key=f"m_a_{slot}_{selected_id}", use_container_width=True): update_stat(selected_id, "assists", -1); st.rerun()

st.divider()

# --- 底部：全隊成績表與匯出區 ---
st.subheader("📈 全隊數據與匯出")

export_data = [
    {"背號": v["number"], "姓名": v["name"], "得分": v["score"], "籃板": v["rebounds"], "助攻": v["assists"]}
    for k, v in st.session_state.roster.items()
]

# 顯示表格
#st.dataframe(export_data, use_container_width=True)

# 匯出按鈕
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

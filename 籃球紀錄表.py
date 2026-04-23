import streamlit as st

st.set_page_config(page_title="籃球五人紀錄台", layout="wide")
st.title("🏀 團隊即時數據紀錄系統 (5人制)")

# 1. 初始化 5 位球員的數據
if 'players' not in st.session_state:
    st.session_state.players = []
    for i in range(5):
        st.session_state.players.append({
            "name": f"球員 {i+1}",
            "number": "00",
            "score": 0,
            "rebounds": 0,
            "assists": 0
        })

# 2. 定義更新函數
def update_stat(p_idx, stat_key, delta):
    new_val = st.session_state.players[p_idx][stat_key] + delta
    if new_val >= 0:
        st.session_state.players[p_idx][stat_key] = new_val

# --- 側邊欄：登記球員資訊 ---
with st.sidebar:
    st.header("📋 球員名單登記")
    for i in range(5):
        st.subheader(f"席位 {i+1}")
        st.session_state.players[i]["name"] = st.text_input(f"姓名", value=st.session_state.players[i]["name"], key=f"edit_n_{i}")
        st.session_state.players[i]["number"] = st.text_input(f"背號", value=st.session_state.players[i]["number"], key=f"edit_num_{i}")
    
    if st.button("🔄 全隊數據歸零", type="primary"):
        for i in range(5):
            st.session_state.players[i].update({"score": 0, "rebounds": 0, "assists": 0})
        st.rerun()

# --- 主畫面：數據看板 ---
st.subheader("📊 全隊即時表現")
cols = st.columns(5)
for i in range(5):
    p = st.session_state.players[i]
    with cols[i]:
        st.metric(label=f"#{p['number']} {p['name']}", value=f"{p['score']} 分", delta=f"R:{p['rebounds']} A:{p['assists']}")

st.divider()

# --- 主畫面：操作區 (使用 Tabs 節省空間) ---
st.subheader("📝 現場即時紀錄")
tabs = st.tabs([f"#{p['number']} {p['name']}" for p in st.session_state.players])

for i, tab in enumerate(tabs):
    with tab:
        p_name = st.session_state.players[i]["name"]
        
        # 建立三個控制區塊
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.write("**得分**")
            if st.button("➕ 加分", key=f"p_s_{i}", use_container_width=True): update_stat(i, "score", 1); st.rerun()
            if st.button("➖ 減分", key=f"m_s_{i}", use_container_width=True): update_stat(i, "score", -1); st.rerun()
            
        with c2:
            st.write("**籃板**")
            if st.button("➕ 籃板", key=f"p_r_{i}", use_container_width=True): update_stat(i, "rebounds", 1); st.rerun()
            if st.button("➖ 修正", key=f"m_r_{i}", use_container_width=True): update_stat(i, "rebounds", -1); st.rerun()
            
        with c3:
            st.write("**助攻**")
            if st.button("➕ 助攻", key=f"p_a_{i}", use_container_width=True): update_stat(i, "assists", 1); st.rerun()
            if st.button("➖ 修正", key=f"m_a_{i}", use_container_width=True): update_stat(i, "assists", -1); st.rerun()
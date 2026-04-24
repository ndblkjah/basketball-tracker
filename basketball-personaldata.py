import streamlit as st
import pandas as pd
import json
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="籃球專業紀錄台", layout="wide")

# 1. 初始化資料結構
if 'roster' not in st.session_state:
    st.session_state.roster = {
        i: {"name": f"球員 {i+1}", "number": f"{i+1:02d}", "score": 0, "rebounds": 0, "assists": 0, "seconds": 0}
        for i in range(9)
    }
if 'active_slots' not in st.session_state:
    st.session_state.active_slots = [0, 1, 2, 3, 4]

# --- 關鍵修正：時間系統變數 ---
if 'clock_running' not in st.session_state:
    st.session_state.clock_running = False
if 'last_timestamp' not in st.session_state:
    st.session_state.last_timestamp = time.time()
if 'total_game_seconds' not in st.session_state:
    st.session_state.total_game_seconds = 0 # 紀錄整場比賽的總秒數，提供給前端計時器使用

# --- 完美版時間計算邏輯 ---
def sync_playing_time():
    """精確計算時間並分配給在場球員，防止時間被吃掉"""
    if st.session_state.clock_running:
        current_time = time.time()
        # 算出包含小數點的精確時間差
        elapsed_exact = current_time - st.session_state.last_timestamp
        elapsed_int = int(elapsed_exact)
        
        # 只有滿 1 秒才進行加總
        if elapsed_int > 0:
            st.session_state.total_game_seconds += elapsed_int # 增加大錶時間
            for slot in st.session_state.active_slots:
                st.session_state.roster[slot]["seconds"] += elapsed_int
            
            # 關鍵：只推進整數秒，保留小數點，這樣頻繁操作才不會流失時間
            st.session_state.last_timestamp += elapsed_int

def format_time(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

# --- 數據與換人觸發函數 ---
def handle_stat(p_id, stat_key, delta):
    sync_playing_time() # 更新數據前先結算時間
    new_val = st.session_state.roster[p_id][stat_key] + delta
    if new_val >= 0:
        st.session_state.roster[p_id][stat_key] = new_val

def handle_sub(slot_idx, new_p_id):
    sync_playing_time() # 換人前先結算前一位球員的時間
    st.session_state.active_slots[slot_idx] = new_p_id

# --- 側邊欄 ---
with st.sidebar:
    st.header("👥 全隊名單設定")
    for i in range(9):
        with st.expander(f"席位 {i+1}：{st.session_state.roster[i]['name']}"):
            st.session_state.roster[i]["name"] = st.text_input("姓名", value=st.session_state.roster[i]["name"], key=f"edit_n_{i}")
            st.session_state.roster[i]["number"] = st.text_input("背號", value=st.session_state.roster[i]["number"], key=f"edit_num_{i}")
    
    if st.button("🔄 全隊數據重置", type="primary"):
        for i in range(9):
            st.session_state.roster[i].update({"score": 0, "rebounds": 0, "assists": 0, "seconds": 0})
        st.session_state.total_game_seconds = 0
        st.session_state.clock_running = False
        st.rerun()

# --- 介面頂部：比賽計時控制 ---
st.title("🏀 專業籃球數據與時間紀錄台")
c1, c2, c3 = st.columns([2, 3, 3])

with c1:
    if st.session_state.clock_running:
        if st.button("⏸️ 暫停計時", use_container_width=True, type="secondary"):
            sync_playing_time()
            st.session_state.clock_running = False
            st.rerun()
    else:
        if st.button("▶️ 開始計時", use_container_width=True, type="primary"):
            st.session_state.last_timestamp = time.time()
            st.session_state.clock_running = True
            st.rerun()

with c2:
    if st.session_state.clock_running:
        # 將 Python 計算的總秒數丟給前端 JS 接手跑動畫
        js_timer_code = f"""
        <div id="live-timer" style="font-size: 1.8rem; font-family: monospace; color: #ff4b4b; font-weight: bold; padding: 5px; border-radius: 8px; background-color: #ffeaea; text-align: center;">
            讀取中...
        </div>
        <script>
            let totalSeconds = {st.session_state.total_game_seconds};
            const timerDiv = document.getElementById('live-timer');
            
            setInterval(() => {{
                totalSeconds++;
                let m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
                let s = (totalSeconds % 60).toString().padStart(2, '0');
                timerDiv.innerText = "⏱️ 計時中 " + m + ":" + s;
            }}, 1000);
        </script>
        """
        components.html(js_timer_code, height=60)
    else:
        # 暫停時直接顯示目前的總時間
        st.markdown(f"<div style='font-size: 1.6rem; text-align: center; color: #888; font-weight: bold; padding: 5px;'>⏸️ 時間已暫停 (目前累積 {format_time(st.session_state.total_game_seconds)})</div>", unsafe_allow_html=True)

with c3:
    if st.button("🕒 強制刷新後端時間", use_container_width=True):
        sync_playing_time()
        st.rerun()

st.divider()

# --- 主畫面：橫式紀錄區 ---
player_options = {i: f"#{st.session_state.roster[i]['number']} {st.session_state.roster[i]['name']}" for i in range(9)}
header_cols = st.columns([2.5, 2.5, 2.5, 2.5])
header_cols[0].markdown("**場上球員 (點擊換人)**")
header_cols[1].markdown("**得分 (Score)**")
header_cols[2].markdown("**籃板 (Rebounds)**")
header_cols[3].markdown("**助攻 (Assists)**")

for slot in range(5):
    with st.container(border=True):
        cols = st.columns([2.5, 2.5, 2.5, 2.5])
        selected_id = st.session_state.active_slots[slot]
        p = st.session_state.roster[selected_id]
        
        with cols[0]:
            with st.popover(f"🔄 {player_options[selected_id]}", use_container_width=True):
                pop_cols = st.columns(2)
                for idx, (opt_id, opt_name) in enumerate(player_options.items()):
                    with pop_cols[idx % 2]:
                        if st.button(opt_name, key=f"sub_{slot}_{opt_id}", use_container_width=True):
                            handle_sub(slot, opt_id)
                            st.rerun()
            st.caption(f"⏱️ 出場時間: {format_time(p['seconds'])}")
            st.caption(f"📊 目前: {p['score']}分 | {p['rebounds']}板 | {p['assists']}助")
        
        for i, key in enumerate(["score", "rebounds", "assists"]):
            with cols[i+1]:
                b1, b2 = st.columns(2)
                b1.button("➕", key=f"p_{key}_{slot}", on_click=handle_stat, args=(selected_id, key, 1), use_container_width=True)
                b2.button("➖", key=f"m_{key}_{slot}", on_click=handle_stat, args=(selected_id, key, -1), use_container_width=True)

st.divider()

# --- 數據總表與匯出 ---
st.subheader("📈 全隊數據總表")
final_data = []
for i in range(9):
    row = st.session_state.roster[i]
    final_data.append({
        "背號": row["number"], "姓名": row["name"], 
        "時間": format_time(row["seconds"]),
        "得分": row["score"], "籃板": row["rebounds"], "助攻": row["assists"]
    })

df = pd.DataFrame(final_data)
st.dataframe(df, use_container_width=True)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    json_string = json.dumps(final_data, ensure_ascii=False, indent=2)
    st.download_button("📥 下載 JSON 檔", file_name="basketball_stats.json", mime="application/json", data=json_string, use_container_width=True)
with col_dl2:
    csv = df.to_csv(index=False).encode('utf-8-sig') 
    st.download_button("📊 下載比賽數據 (Excel CSV)", file_name="basketball_stats.csv", mime="text/csv", data=csv, use_container_width=True)
